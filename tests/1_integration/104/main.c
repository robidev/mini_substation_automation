/*
 * main.c – ncurses TUI for the IEC 60870-5-104 Master
 *
 * Layout:
 *   ┌──────────────────── STATUS ─────────────────────────────────────┐
 *   │ Host: …  Port: …  State: …  CA: …  Tx: …  Rx: …              │
 *   ├──────────────────── EVENTS ─────────────────────────────────────┤
 *   │  #  Time      Type         COT    CA    IOA       Value  Quality│
 *   │  …                                                              │
 *   │  …                                                              │
 *   ├──────────────────── COMMAND ────────────────────────────────────┤
 *   │ > _                                                             │
 *   ├──────────────────── HELP ───────────────────────────────────────┤
 *   │ connect <ip> [port] [ca]  gi  dc <ioa> <1|2> [sel]  quit       │
 *   └─────────────────────────────────────────────────────────────────┘
 *
 * Commands (case-insensitive):
 *   connect <ip> [port=2404] [ca=1]
 *   disconnect
 *   gi                           – send General Interrogation
 *   dc <ioa> <1|2> [sel=0]       – send Double Command (1=OFF, 2=ON)
 *   ca <value>                   – change Common Address
 *   clear                        – clear event log
 *   quit / exit
 */

#include <ncurses.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <ctype.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>

#include "iec104.h"

/* ─── Globals ─────────────────────────────────────────────────────────── */
static iec104_master_t  g_master;
static volatile int     g_running = 1;

/* ─── Ncurses windows ─────────────────────────────────────────────────── */
static WINDOW *w_status  = NULL;
static WINDOW *w_events  = NULL;
static WINDOW *w_cmd     = NULL;
static WINDOW *w_help    = NULL;

#define STATUS_H   3
#define HELP_H     3
#define CMD_H      3

/* ─── Colors ──────────────────────────────────────────────────────────── */
#define C_TITLE      1
#define C_STATUS_OK  2
#define C_STATUS_ERR 3
#define C_EVENT_SPONT 4
#define C_EVENT_CTRL  5
#define C_EVENT_RESP  6
#define C_HEADER     7
#define C_DIM        8
#define C_PROMPT     9

/* ─── Command history ─────────────────────────────────────────────────── */
#define HISTORY_MAX 32
static char cmd_history[HISTORY_MAX][256];
static int  history_len = 0;
static int  history_pos = -1;

/* ─── Event display offset (scroll) ─────────────────────────────────────*/
static int ev_scroll = 0;   /* 0 = bottom (newest), positive = scrolled up */

/* ─── Helpers ─────────────────────────────────────────────────────────── */
static void str_toupper_copy(char *dst, const char *src, size_t sz)
{
    for (size_t i = 0; i < sz-1 && src[i]; i++)
        dst[i] = toupper((unsigned char)src[i]);
    dst[sz-1] = 0;
}

static const char *cot_color_pair(uint8_t cot)
{
    (void)cot;
    return NULL;
}
static int cot_color(uint8_t cot)
{
    switch (cot) {
    case COT_SPONTANEOUS: return C_EVENT_SPONT;
    case COT_ACTIVATION:
    case COT_DEACTIVATION: return C_EVENT_CTRL;
    case COT_ACTCON:
    case COT_DEACTCON:
    case COT_ACTTERM: return C_EVENT_RESP;
    default: return C_DIM;
    }
    (void)cot_color_pair(0);
}

static void draw_border_title(WINDOW *w, const char *title, int color)
{
    box(w, 0, 0);
    int width = getmaxx(w);
    int tlen  = strlen(title);
    int tx    = (width - tlen - 2) / 2;
    if (tx < 1) tx = 1;
    wattron(w, COLOR_PAIR(color) | A_BOLD);
    mvwprintw(w, 0, tx, " %s ", title);
    wattroff(w, COLOR_PAIR(color) | A_BOLD);
}

/* ─── Layout rebuild ──────────────────────────────────────────────────── */
static void rebuild_layout(void)
{
    if (w_status)  { delwin(w_status);  w_status  = NULL; }
    if (w_events)  { delwin(w_events);  w_events  = NULL; }
    if (w_cmd)     { delwin(w_cmd);     w_cmd     = NULL; }
    if (w_help)    { delwin(w_help);    w_help    = NULL; }

    int rows, cols;
    getmaxyx(stdscr, rows, cols);

    int ev_h = rows - STATUS_H - CMD_H - HELP_H;
    if (ev_h < 4) ev_h = 4;

    int y = 0;
    w_status = newwin(STATUS_H, cols, y, 0);            y += STATUS_H;
    w_events = newwin(ev_h,     cols, y, 0);            y += ev_h;
    w_cmd    = newwin(CMD_H,    cols, y, 0);            y += CMD_H;
    w_help   = newwin(HELP_H,   cols, y, 0);

    scrollok(w_events, FALSE);
}

/* ─── Draw status ─────────────────────────────────────────────────────── */
static void draw_status(void)
{
    werase(w_status);
    draw_border_title(w_status, "IEC 60870-5-104 MASTER", C_TITLE);

    const char *state = iec104_state_name(g_master.state);
    int sc = (g_master.state == STATE_STARTED)  ? C_STATUS_OK :
             (g_master.state == STATE_ERROR)     ? C_STATUS_ERR : C_DIM;

    mvwprintw(w_status, 1, 2, "Host: %-20s Port: %-6d CA: %-5u  State: ",
              g_master.host[0] ? g_master.host : "-",
              g_master.port ? g_master.port : 2404,
              g_master.common_addr);

    wattron(w_status, COLOR_PAIR(sc) | A_BOLD);
    wprintw(w_status, "%-14s", state);
    wattroff(w_status, COLOR_PAIR(sc) | A_BOLD);

    wprintw(w_status, "  Tx: %-6llu Rx: %-6llu  I-rx: %-5llu",
            (unsigned long long)g_master.frames_tx,
            (unsigned long long)g_master.frames_rx,
            (unsigned long long)g_master.i_frames_rx);

    wnoutrefresh(w_status);
}

/* ─── Draw events ─────────────────────────────────────────────────────── */
static void draw_events(void)
{
    werase(w_events);
    draw_border_title(w_events, "EVENT LOG", C_TITLE);

    int ev_h  = getmaxy(w_events);
    int ev_w  = getmaxx(w_events);
    int rows  = ev_h - 2;   /* inside border */

    /* header row */
    wattron(w_events, COLOR_PAIR(C_HEADER) | A_BOLD);
    mvwprintw(w_events, 1, 2,
              "%-5s %-8s %-14s %-9s %-5s %-8s %-18s %-10s %s",
              "#", "Time", "Type", "COT", "CA", "IOA", "Value", "Quality",
              "Timestamp");
    wattroff(w_events, COLOR_PAIR(C_HEADER) | A_BOLD);

    int display_rows = rows - 1;   /* rows available for data */
    int total = g_master.event_count;

    /* scroll: 0=latest at bottom */
    int start_idx = total - display_rows - ev_scroll;
    if (start_idx < 0) start_idx = 0;

    int row = 2;
    for (int i = start_idx; i < total && row < ev_h - 1; i++, row++) {
        int ring_idx = (g_master.event_head - total + i) % MAX_EVENTS;
        if (ring_idx < 0) ring_idx += MAX_EVENTS;
        event_record_t *ev = &g_master.events[ring_idx];

        struct tm *tm = localtime(&ev->recv_time);
        char tmbuf[16];
        strftime(tmbuf, sizeof(tmbuf), "%H:%M:%S", tm);

        int pair = cot_color(ev->cot);
        wattron(w_events, COLOR_PAIR(pair));

        /* truncate value to fit */
        char val_trunc[20];
        snprintf(val_trunc, sizeof(val_trunc), "%s", ev->value_str);

        mvwprintw(w_events, row, 2,
                  "%-5d %-8s %-14s %-9s %-5u %-8u %-18s %-10s %s",
                  i + 1, tmbuf,
                  iec104_type_name(ev->type_id),
                  iec104_cot_name(ev->cot),
                  ev->ca, ev->ioa,
                  val_trunc,
                  ev->quality_str,
                  ev->timestamp_str);
        wattroff(w_events, COLOR_PAIR(pair));

        /* clamp to window width */
        if (getmaxx(w_events) > 0)
            mvwchgat(w_events, row, ev_w - 1, 1, A_NORMAL, 0, NULL);
    }

    /* scroll indicator */
    if (ev_scroll > 0) {
        wattron(w_events, COLOR_PAIR(C_DIM) | A_BOLD);
        mvwprintw(w_events, ev_h - 1, ev_w - 20, " [scroll -%d] ", ev_scroll);
        wattroff(w_events, COLOR_PAIR(C_DIM) | A_BOLD);
    }

    wnoutrefresh(w_events);
    (void)cot_color_pair(0);
}

/* ─── Draw help ───────────────────────────────────────────────────────── */
static void draw_help(void)
{
    werase(w_help);
    draw_border_title(w_help, "HELP", C_TITLE);
    wattron(w_help, COLOR_PAIR(C_DIM));
    mvwprintw(w_help, 1, 2,
        "connect <ip> [port=2404] [ca=1]  |  disconnect  |  gi  |  "
        "dc <ioa> <1|2> [sel]  |  ca <val>  |  clear  |  quit");
    mvwprintw(w_help, 2, 2,
        "PgUp/PgDn: scroll events  |  F5: force redraw");
    wattroff(w_help, COLOR_PAIR(C_DIM));
    wnoutrefresh(w_help);
}

/* ─── Message display in cmd window ──────────────────────────────────── */
static void cmd_msg(const char *msg, int is_err)
{
    werase(w_cmd);
    draw_border_title(w_cmd, "COMMAND", C_TITLE);
    wattron(w_cmd, COLOR_PAIR(is_err ? C_STATUS_ERR : C_STATUS_OK));
    mvwprintw(w_cmd, 1, 2, "%s", msg);
    wattroff(w_cmd, COLOR_PAIR(is_err ? C_STATUS_ERR : C_STATUS_OK));
    wnoutrefresh(w_cmd);
    doupdate();
}

/* ─── Command line editing widget ────────────────────────────────────── */
#define MAX_CMD_LEN 200

static char cmd_buf[MAX_CMD_LEN + 1];
static int  cmd_pos   = 0;
static int  cmd_len   = 0;

static void cmd_redraw(void)
{
    werase(w_cmd);
    draw_border_title(w_cmd, "COMMAND", C_TITLE);
    wattron(w_cmd, COLOR_PAIR(C_PROMPT) | A_BOLD);
    mvwprintw(w_cmd, 1, 2, "> ");
    wattroff(w_cmd, COLOR_PAIR(C_PROMPT) | A_BOLD);
    mvwprintw(w_cmd, 1, 4, "%.*s", MAX_CMD_LEN, cmd_buf);
    wmove(w_cmd, 1, 4 + cmd_pos);
    wrefresh(w_cmd);
}

/* ─── Command processor ───────────────────────────────────────────────── */
static void process_cmd(char *line)
{
    /* strip leading/trailing whitespace */
    while (*line == ' ') line++;
    int l = strlen(line);
    while (l > 0 && (line[l-1] == ' ' || line[l-1] == '\n')) line[--l] = 0;
    if (!*line) return;

    /* save to history */
    if (history_len < HISTORY_MAX) {
        strncpy(cmd_history[history_len++], line, 255);
    } else {
        memmove(cmd_history[0], cmd_history[1], 255 * (HISTORY_MAX-1));
        strncpy(cmd_history[HISTORY_MAX-1], line, 255);
    }
    history_pos = -1;

    char tok[16];
    str_toupper_copy(tok, line, sizeof(tok));

    /* ── CONNECT ──────────────────────────────────────── */
    if (strncmp(tok, "CONNECT", 7) == 0) {
        char host[128] = "127.0.0.1";
        int  port = 2404;
        int  ca   = 1;
        sscanf(line + 7, " %127s %d %d", host, &port, &ca);

        if (g_master.state != STATE_DISCONNECTED && g_master.state != STATE_ERROR) {
            iec104_disconnect(&g_master);
        }
        iec104_init(&g_master, host, port, (uint16_t)ca);
        if (iec104_connect(&g_master) < 0) {
            cmd_msg("ERROR: connect failed", 1);
        } else {
            cmd_msg("Connecting…", 0);
        }
        return;
    }

    /* ── DISCONNECT ───────────────────────────────────── */
    if (strcmp(tok, "DISCONNECT") == 0) {
        iec104_disconnect(&g_master);
        cmd_msg("Disconnected.", 0);
        return;
    }

    /* ── GI ───────────────────────────────────────────── */
    if (strcmp(tok, "GI") == 0) {
        if (iec104_send_gi(&g_master) < 0)
            cmd_msg("ERROR: not in STARTED state", 1);
        else
            cmd_msg("GI sent.", 0);
        return;
    }

    /* ── DC <ioa> <1|2> [sel] ─────────────────────────── */
    if (strncmp(tok, "DC", 2) == 0) {
        unsigned ioa  = 0;
        int      dcs  = 0;
        int      sel  = 0;
        int parsed = sscanf(line + 2, " %u %d %d", &ioa, &dcs, &sel);
        if (parsed < 2 || dcs < 1 || dcs > 2) {
            cmd_msg("Usage: dc <ioa> <1=OFF|2=ON> [sel=0]", 1);
            return;
        }
        if (iec104_send_double_cmd(&g_master, ioa, (uint8_t)dcs, sel) < 0)
            cmd_msg("ERROR: not in STARTED state", 1);
        else {
            char msg[64];
            snprintf(msg, sizeof(msg), "Double cmd sent: IOA=%u DCS=%s S/E=%d",
                     ioa, dcs == 2 ? "ON(2)" : "OFF(1)", sel);
            cmd_msg(msg, 0);
        }
        return;
    }

    /* ── CA <value> ───────────────────────────────────── */
    if (strncmp(tok, "CA", 2) == 0) {
        int ca = 0;
        sscanf(line + 2, " %d", &ca);
        g_master.common_addr = (uint16_t)ca;
        char msg[32];
        snprintf(msg, sizeof(msg), "CA set to %d", ca);
        cmd_msg(msg, 0);
        return;
    }

    /* ── CLEAR ────────────────────────────────────────── */
    if (strcmp(tok, "CLEAR") == 0) {
        g_master.event_count = 0;
        g_master.event_head  = 0;
        ev_scroll = 0;
        cmd_msg("Event log cleared.", 0);
        return;
    }

    /* ── QUIT / EXIT ──────────────────────────────────── */
    if (strcmp(tok, "QUIT") == 0 || strcmp(tok, "EXIT") == 0) {
        g_running = 0;
        return;
    }

    cmd_msg("Unknown command. See help below.", 1);
}

/* ─── Signal handler ──────────────────────────────────────────────────── */
static void handle_sigint(int sig)
{
    (void)sig;
    g_running = 0;
}

/* ─── Main ────────────────────────────────────────────────────────────── */
int main(int argc, char *argv[])
{
    signal(SIGINT,  handle_sigint);
    signal(SIGTERM, handle_sigint);
    signal(SIGPIPE, SIG_IGN);

    /* Optional CLI args: ./iec104_master <host> [port] [ca] */
    const char *cli_host = NULL;
    int         cli_port = 2404;
    int         cli_ca   = 1;
    if (argc >= 2) { cli_host = argv[1]; }
    if (argc >= 3) { cli_port = atoi(argv[2]); }
    if (argc >= 4) { cli_ca   = atoi(argv[3]); }

    /* Init master state */
    iec104_init(&g_master, cli_host ? cli_host : "", cli_port, (uint16_t)cli_ca);

    /* ncurses init */
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    nodelay(stdscr, TRUE);
    curs_set(1);

    if (has_colors()) {
        start_color();
        use_default_colors();
        init_pair(C_TITLE,       COLOR_CYAN,    -1);
        init_pair(C_STATUS_OK,   COLOR_GREEN,   -1);
        init_pair(C_STATUS_ERR,  COLOR_RED,     -1);
        init_pair(C_EVENT_SPONT, COLOR_YELLOW,  -1);
        init_pair(C_EVENT_CTRL,  COLOR_MAGENTA, -1);
        init_pair(C_EVENT_RESP,  COLOR_GREEN,   -1);
        init_pair(C_HEADER,      COLOR_WHITE,   -1);
        init_pair(C_DIM,         COLOR_WHITE,   -1);
        init_pair(C_PROMPT,      COLOR_CYAN,    -1);
    }

    rebuild_layout();

    /* auto-connect if host given */
    if (cli_host) {
        if (iec104_connect(&g_master) < 0) {
            /* will show in status */
        }
    }

    /* ── Main loop ───────────────────────────────────── */
    time_t last_tick   = time(NULL);
    time_t last_redraw = 0;

    while (g_running) {
        /* ── Network poll ─────────────── */
        iec104_poll(&g_master);

        /* ── Timer tick ──────────────── */
        time_t now = time(NULL);
        if (now != last_tick) {
            iec104_tick(&g_master);
            last_tick = now;
        }

        /* ── Input ───────────────────── */
        int ch = getch();
        switch (ch) {
        case ERR: break;   /* no input */

        case KEY_RESIZE:
        case KEY_F(5):
            rebuild_layout();
            ev_scroll = 0;
            break;

        case KEY_PPAGE:    /* Page Up – scroll up */
            ev_scroll += (getmaxy(w_events) - 3);
            if (ev_scroll > g_master.event_count - 1)
                ev_scroll = g_master.event_count - 1;
            break;

        case KEY_NPAGE:    /* Page Down – scroll down */
            ev_scroll -= (getmaxy(w_events) - 3);
            if (ev_scroll < 0) ev_scroll = 0;
            break;

        case KEY_UP: {
            int hi = history_pos < 0 ? history_len - 1 : history_pos - 1;
            if (hi >= 0) {
                history_pos = hi;
                strncpy(cmd_buf, cmd_history[hi], MAX_CMD_LEN);
                cmd_len = cmd_pos = strlen(cmd_buf);
            }
            break;
        }
        case KEY_DOWN: {
            if (history_pos >= 0) {
                history_pos++;
                if (history_pos >= history_len) {
                    history_pos = -1;
                    cmd_buf[0] = 0; cmd_len = cmd_pos = 0;
                } else {
                    strncpy(cmd_buf, cmd_history[history_pos], MAX_CMD_LEN);
                    cmd_len = cmd_pos = strlen(cmd_buf);
                }
            }
            break;
        }
        case KEY_LEFT:
            if (cmd_pos > 0) cmd_pos--;
            break;
        case KEY_RIGHT:
            if (cmd_pos < cmd_len) cmd_pos++;
            break;
        case KEY_HOME:
            cmd_pos = 0;
            break;
        case KEY_END:
            cmd_pos = cmd_len;
            break;

        case KEY_BACKSPACE:
        case 127:
        case '\b':
            if (cmd_pos > 0) {
                memmove(cmd_buf + cmd_pos - 1, cmd_buf + cmd_pos, cmd_len - cmd_pos + 1);
                cmd_pos--; cmd_len--;
            }
            break;
        case KEY_DC:
            if (cmd_pos < cmd_len) {
                memmove(cmd_buf + cmd_pos, cmd_buf + cmd_pos + 1, cmd_len - cmd_pos);
                cmd_len--;
            }
            break;

        case '\n':
        case '\r':
        case KEY_ENTER: {
            char line[MAX_CMD_LEN + 1];
            strncpy(line, cmd_buf, MAX_CMD_LEN);
            cmd_buf[0] = 0; cmd_len = cmd_pos = 0;
            process_cmd(line);
            break;
        }

        default:
            if (ch >= 32 && ch < 127 && cmd_len < MAX_CMD_LEN) {
                memmove(cmd_buf + cmd_pos + 1, cmd_buf + cmd_pos, cmd_len - cmd_pos + 1);
                cmd_buf[cmd_pos++] = (char)ch;
                cmd_len++;
            }
            break;
        }

        /* ── Redraw (max ~20fps) ─────── */
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        long now_ms = ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
        if (now_ms - last_redraw > 50) {
            last_redraw = now_ms;
            draw_status();
            draw_events();
            draw_help();
            cmd_redraw();
            doupdate();
        }

        /* ── Sleep a bit ─────────────── */
        usleep(10000);   /* 10ms */
    }

    /* cleanup */
    iec104_disconnect(&g_master);
    endwin();

    printf("\nDisconnected. Goodbye.\n");
    return 0;
}
