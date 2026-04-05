/*
 * iec104.c – IEC 60870-5-104 Master implementation
 *
 * Supports:
 *   – TCP connect / STARTDT handshake
 *   – I / S / U frame send & receive
 *   – T1 / T2 / T3 timers
 *   – General Interrogation (TI 100)
 *   – Double Command (TI 46)
 *   – Spontaneous event parsing (TI 1,3,5,7,9,11,13,30,31,34,35,36,70)
 *   – CP56Time2a decoding
 */

#include "iec104.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <netdb.h>

/* ────────────────────────────────────────────────────────────────────── */
/* Helpers                                                                */
/* ────────────────────────────────────────────────────────────────────── */

static uint32_t decode_ioa(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16);
}

static void decode_cp56(const uint8_t *p, char *out, size_t sz)
{
    uint16_t ms   = (uint16_t)p[0] | ((uint16_t)p[1] << 8);
    uint8_t  min  = p[2] & 0x3F;
    int      iv   = (p[2] >> 7) & 1;
    uint8_t  hour = p[3] & 0x1F;
    int      su   = (p[3] >> 7) & 1;
    uint8_t  dom  = p[4] & 0x1F;
    uint8_t  mon  = p[5] & 0x0F;
    uint8_t  year = p[6] & 0x7F;
    snprintf(out, sz, "20%02u-%02u-%02u %02u:%02u:%06.3f%s%s",
             year, mon, dom, hour, min, ms / 1000.0,
             su  ? " SU"  : "",
             iv  ? " IV"  : "");
}

static void decode_quality(uint8_t q, char *out, size_t sz)
{
    char buf[64] = "";
    if (q == 0) { snprintf(out, sz, "OK"); return; }
    if (q & QDS_IV) strncat(buf, "IV ", sz-1);
    if (q & QDS_NT) strncat(buf, "NT ", sz-1);
    if (q & QDS_SB) strncat(buf, "SB ", sz-1);
    if (q & QDS_BL) strncat(buf, "BL ", sz-1);
    if (q & QDS_OV) strncat(buf, "OV ", sz-1);
    int l = strlen(buf);
    if (l > 0 && buf[l-1] == ' ') buf[l-1] = 0;
    snprintf(out, sz, "%s", buf[0] ? buf : "?");
}

/* ────────────────────────────────────────────────────────────────────── */
/* Name tables                                                            */
/* ────────────────────────────────────────────────────────────────────── */

const char *iec104_type_name(uint8_t t)
{
    switch(t) {
    case TI_M_SP_NA_1: return "M_SP_NA_1";
    case TI_M_DP_NA_1: return "M_DP_NA_1";
    case TI_M_ST_NA_1: return "M_ST_NA_1";
    case TI_M_BO_NA_1: return "M_BO_NA_1";
    case TI_M_ME_NA_1: return "M_ME_NA_1";
    case TI_M_ME_NB_1: return "M_ME_NB_1";
    case TI_M_ME_NC_1: return "M_ME_NC_1";
    case TI_M_IT_NA_1: return "M_IT_NA_1";
    case TI_M_SP_TB_1: return "M_SP_TB_1";
    case TI_M_DP_TB_1: return "M_DP_TB_1";
    case TI_M_ME_TD_1: return "M_ME_TD_1";
    case TI_M_ME_TE_1: return "M_ME_TE_1";
    case TI_M_ME_TF_1: return "M_ME_TF_1";
    case TI_C_SC_NA_1: return "C_SC_NA_1";
    case TI_C_DC_NA_1: return "C_DC_NA_1";
    case TI_C_RC_NA_1: return "C_RC_NA_1";
    case TI_C_SC_TA_1: return "C_SC_TA_1";
    case TI_C_DC_TA_1: return "C_DC_TA_1";
    case TI_C_IC_NA_1: return "C_IC_NA_1";
    case TI_C_CI_NA_1: return "C_CI_NA_1";
    case TI_M_EI_NA_1: return "M_EI_NA_1";
    default: { static char buf[16]; snprintf(buf,sizeof(buf),"TI_%u",t); return buf; }
    }
}

const char *iec104_cot_name(uint8_t c)
{
    switch(c) {
    case COT_PERIODIC:    return "Per";
    case COT_BACKGROUND:  return "Back";
    case COT_SPONTANEOUS: return "Spont";
    case COT_INITIALIZED: return "Init";
    case COT_REQUEST:     return "Req";
    case COT_ACTIVATION:  return "Act";
    case COT_ACTCON:      return "ActCon";
    case COT_DEACTIVATION:return "Deact";
    case COT_DEACTCON:    return "DeactCon";
    case COT_ACTTERM:     return "ActTerm";
    case COT_INROGEN:     return "InroGen";
    case COT_REQCOGEN:    return "ReqCoGen";
    case COT_UNKNOWN_TYPE:return "UnkType";
    case COT_UNKNOWN_COT: return "UnkCot";
    case COT_UNKNOWN_CA:  return "UnkCA";
    case COT_UNKNOWN_IOA: return "UnkIOA";
    default: { static char buf[16]; snprintf(buf,sizeof(buf),"COT_%u",c); return buf; }
    }
}

const char *iec104_state_name(conn_state_t s)
{
    switch(s) {
    case STATE_DISCONNECTED: return "DISCONNECTED";
    case STATE_CONNECTING:   return "CONNECTING";
    case STATE_CONNECTED:    return "CONNECTED";
    case STATE_STARTED:      return "STARTED";
    case STATE_STOPPING:     return "STOPPING";
    case STATE_ERROR:        return "ERROR";
    default: return "UNKNOWN";
    }
}

/* ────────────────────────────────────────────────────────────────────── */
/* Init / Connect / Disconnect                                            */
/* ────────────────────────────────────────────────────────────────────── */

void iec104_init(iec104_master_t *m, const char *host, int port, uint16_t ca)
{
    memset(m, 0, sizeof(*m));
    strncpy(m->host, host, sizeof(m->host)-1);
    m->port        = port;
    m->common_addr = ca;
    m->sock        = -1;
    m->state       = STATE_DISCONNECTED;
    m->t1_seconds  = 15;
    m->t2_seconds  = 10;
    m->t3_seconds  = 20;
    m->w           = 8;
}

int iec104_connect(iec104_master_t *m)
{
    struct addrinfo hints, *res, *rp;
    char port_str[16];
    int fd, flags, ret;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family   = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    snprintf(port_str, sizeof(port_str), "%d", m->port);

    ret = getaddrinfo(m->host, port_str, &hints, &res);
    if (ret != 0) return -1;

    fd = -1;
    for (rp = res; rp; rp = rp->ai_next) {
        fd = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (fd < 0) continue;

        /* non-blocking */
        flags = fcntl(fd, F_GETFL, 0);
        fcntl(fd, F_SETFL, flags | O_NONBLOCK);

        /* TCP keepalive & nodelay */
        int opt = 1;
        setsockopt(fd, IPPROTO_TCP, TCP_NODELAY,   &opt, sizeof(opt));
        setsockopt(fd, SOL_SOCKET,  SO_KEEPALIVE,  &opt, sizeof(opt));

        if (connect(fd, rp->ai_addr, rp->ai_addrlen) < 0) {
            if (errno != EINPROGRESS) {
                close(fd); fd = -1; continue;
            }
        }
        break;
    }
    freeaddrinfo(res);

    if (fd < 0) return -1;

    m->sock          = fd;
    m->state         = STATE_CONNECTING;
    m->send_sn       = 0;
    m->recv_sn       = 0;
    m->ack_sn        = 0;
    m->t3_last_rx    = time(NULL);
    m->frames_tx     = 0;
    m->frames_rx     = 0;
    return 0;
}

void iec104_disconnect(iec104_master_t *m)
{
    if (m->sock >= 0) {
        close(m->sock);
        m->sock = -1;
    }
    m->state = STATE_DISCONNECTED;
    m->send_sn = m->recv_sn = m->ack_sn = 0;
    m->unacked_recv = 0;
}

/* ────────────────────────────────────────────────────────────────────── */
/* Low-level frame send                                                   */
/* ────────────────────────────────────────────────────────────────────── */

static int send_raw(iec104_master_t *m, const uint8_t *buf, int len)
{
    int sent = 0;
    while (sent < len) {
        int r = write(m->sock, buf + sent, len - sent);
        if (r < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        sent += r;
    }
    m->frames_tx++;
    return 0;
}

static int send_u_frame(iec104_master_t *m, uint8_t func)
{
    uint8_t buf[6] = { START_BYTE, 4, func, 0, 0, 0 };
    return send_raw(m, buf, 6);
}

static int send_s_frame(iec104_master_t *m)
{
    uint8_t buf[6];
    buf[0] = START_BYTE;
    buf[1] = 4;
    buf[2] = 0x01;  /* S-frame marker */
    buf[3] = 0x00;
    buf[4] = (m->recv_sn << 1) & 0xFE;
    buf[5] = (m->recv_sn >> 7) & 0xFF;
    m->unacked_recv = 0;
    return send_raw(m, buf, 6);
}

/* Build and send an I-frame with given ASDU payload */
static int send_i_frame(iec104_master_t *m, const uint8_t *asdu, int asdu_len)
{
    if (m->state != STATE_STARTED) return -1;

    uint8_t buf[MAX_APDU_LEN + 2];
    buf[0] = START_BYTE;
    buf[1] = (uint8_t)(4 + asdu_len);

    /* control field: send SN (bits 15..1, bit0=0) */
    buf[2] = (m->send_sn << 1) & 0xFE;
    buf[3] = (m->send_sn >> 7) & 0xFF;
    /* control field: recv SN */
    buf[4] = (m->recv_sn << 1) & 0xFE;
    buf[5] = (m->recv_sn >> 7) & 0xFF;

    memcpy(buf + 6, asdu, asdu_len);

    if (send_raw(m, buf, 6 + asdu_len) < 0) return -1;

    m->send_sn = (m->send_sn + 1) & 0x7FFF;
    m->i_frames_rx++;   /* reuse counter – or add separate tx counter */
    m->unacked_recv = 0;
    return 0;
}

/* ────────────────────────────────────────────────────────────────────── */
/* Public send commands                                                   */
/* ────────────────────────────────────────────────────────────────────── */

int iec104_start_dt(iec104_master_t *m)
{
    if (m->state != STATE_CONNECTED && m->state != STATE_CONNECTING)
        return -1;
    m->t1_start = time(NULL);
    return send_u_frame(m, U_STARTDT_ACT);
}

int iec104_send_gi(iec104_master_t *m)
{
    /* C_IC_NA_1: ASDU = header(6) + IOA(3=0) + QOI(1=20) = 10 bytes */
    uint8_t asdu[10];
    asdu[0] = TI_C_IC_NA_1;
    asdu[1] = 0x01;               /* 1 object, SQ=0 */
    asdu[2] = COT_ACTIVATION;
    asdu[3] = 0x00;               /* originator addr */
    asdu[4] = m->common_addr & 0xFF;
    asdu[5] = (m->common_addr >> 8) & 0xFF;
    asdu[6] = 0x00;               /* IOA = 0 */
    asdu[7] = 0x00;
    asdu[8] = 0x00;
    asdu[9] = QOI_GENERAL;
    return send_i_frame(m, asdu, 10);
}

int iec104_send_double_cmd(iec104_master_t *m, uint32_t ioa, uint8_t dcs, int select)
{
    /* C_DC_NA_1: ASDU = header(6) + IOA(3) + DCO(1) = 10 bytes */
    uint8_t asdu[10];
    asdu[0] = TI_C_DC_NA_1;
    asdu[1] = 0x01;
    asdu[2] = COT_ACTIVATION;
    asdu[3] = 0x00;
    asdu[4] = m->common_addr & 0xFF;
    asdu[5] = (m->common_addr >> 8) & 0xFF;
    asdu[6] = ioa & 0xFF;
    asdu[7] = (ioa >> 8) & 0xFF;
    asdu[8] = (ioa >> 16) & 0xFF;
    /* DCO: bits 0-1 = DCS, bit7 = S/E */
    asdu[9] = (dcs & 0x03) | (select ? 0x80 : 0x00);
    return send_i_frame(m, asdu, 10);
}

/* ────────────────────────────────────────────────────────────────────── */
/* ASDU parser / event logger                                             */
/* ────────────────────────────────────────────────────────────────────── */

static void log_event(iec104_master_t *m, event_record_t *ev)
{
    int idx = m->event_head % MAX_EVENTS;
    memcpy(&m->events[idx], ev, sizeof(*ev));
    m->event_head++;
    if (m->event_count < MAX_EVENTS) m->event_count++;
}

static void parse_asdu(iec104_master_t *m, const uint8_t *data, int len,
                        const uint8_t *raw_apdu, int raw_len)
{
    if (len < 6) return;

    uint8_t  type_id   = data[0];
    uint8_t  vsq       = data[1];
    uint8_t  sq        = (vsq >> 7) & 1;
    uint8_t  num_obj   = vsq & 0x7F;
    uint8_t  cot       = data[2] & 0x3F;
    /* uint8_t  pn       = (data[2] >> 6) & 1; */
    /* uint8_t  test     = (data[2] >> 7) & 1; */
    uint16_t ca        = (uint16_t)data[4] | ((uint16_t)data[5] << 8);

    const uint8_t *p = data + 6;
    int remaining    = len - 6;

    for (int i = 0; i < num_obj && remaining > 0; i++) {

        event_record_t ev;
        memset(&ev, 0, sizeof(ev));
        ev.recv_time = time(NULL);
        ev.type_id   = type_id;
        ev.cot       = cot;
        ev.ca        = ca;
        memcpy(ev.raw, raw_apdu, raw_len < MAX_APDU_LEN ? raw_len : MAX_APDU_LEN);
        ev.raw_len   = raw_len;

        /* IOA: first object has explicit 3-byte IOA;
           SQ=1 means subsequent objects increment IOA by 1 */
        uint32_t ioa;
        if (!sq || i == 0) {
            if (remaining < 3) break;
            ioa = decode_ioa(p);
            p += 3; remaining -= 3;
        } else {
            ioa = ev.ioa + 1;
        }
        ev.ioa = ioa;

        /* parse object by type */
        switch (type_id) {

        /* ── Single-point ─────────────────────────────── */
        case TI_M_SP_NA_1: {
            if (remaining < 1) goto done;
            uint8_t siq = *p++;  remaining--;
            uint8_t spi = siq & 0x01;
            decode_quality(siq & 0xF0, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%s", spi ? "ON" : "OFF");
            break;
        }

        /* ── Double-point ─────────────────────────────── */
        case TI_M_DP_NA_1: {
            if (remaining < 1) goto done;
            uint8_t diq = *p++;  remaining--;
            uint8_t dpi = diq & 0x03;
            const char *dpi_str[] = {"Indeterminate/0","OFF","ON","Indeterminate/3"};
            decode_quality(diq & 0xF0, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%s", dpi_str[dpi]);
            break;
        }

        /* ── Step position ────────────────────────────── */
        case TI_M_ST_NA_1: {
            if (remaining < 2) goto done;
            uint8_t vti = *p++;  remaining--;
            uint8_t qds = *p++;  remaining--;
            int  val   = (int8_t)(vti & 0x7F);   /* sign-extend 7-bit */
            int  t_bit = (vti >> 7) & 1;
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%d%s", val, t_bit ? " T" : "");
            break;
        }

        /* ── Bitstring 32 ─────────────────────────────── */
        case TI_M_BO_NA_1: {
            if (remaining < 5) goto done;
            uint32_t bs = (uint32_t)p[0] | ((uint32_t)p[1]<<8) |
                          ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
            uint8_t qds = p[4];
            p += 5; remaining -= 5;
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "0x%08X", bs);
            break;
        }

        /* ── Measured normalised ──────────────────────── */
        case TI_M_ME_NA_1: {
            if (remaining < 3) goto done;
            int16_t raw = (int16_t)((uint16_t)p[0] | ((uint16_t)p[1]<<8));
            uint8_t qds = p[2];
            p += 3; remaining -= 3;
            float val = raw / 32767.0f;
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%.5f (raw %d)", val, raw);
            break;
        }

        /* ── Measured scaled ──────────────────────────── */
        case TI_M_ME_NB_1: {
            if (remaining < 3) goto done;
            int16_t raw = (int16_t)((uint16_t)p[0] | ((uint16_t)p[1]<<8));
            uint8_t qds = p[2];
            p += 3; remaining -= 3;
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%d", (int)raw);
            break;
        }

        /* ── Measured short float ─────────────────────── */
        case TI_M_ME_NC_1: {
            if (remaining < 5) goto done;
            float val;
            memcpy(&val, p, 4);
            uint8_t qds = p[4];
            p += 5; remaining -= 5;
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%.6g", (double)val);
            break;
        }

        /* ── Integrated totals ────────────────────────── */
        case TI_M_IT_NA_1: {
            if (remaining < 5) goto done;
            uint32_t cnt = (uint32_t)p[0] | ((uint32_t)p[1]<<8) |
                           ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
            uint8_t  bcr = p[4];   /* bit 5=CA, 6=CY, 7=IV */
            p += 5; remaining -= 5;
            decode_quality(bcr & 0xE0, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%u seq=%u%s%s",
                     cnt & 0x1FFFFFFF, cnt >> 29,
                     (bcr & 0x40) ? " CY" : "",
                     (bcr & 0x20) ? " CA" : "");
            break;
        }

        /* ── Single-point with CP56Time2a ─────────────── */
        case TI_M_SP_TB_1: {
            if (remaining < 8) goto done;
            uint8_t siq = *p++;  remaining--;
            uint8_t spi = siq & 0x01;
            decode_quality(siq & 0xF0, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%s", spi ? "ON" : "OFF");
            decode_cp56(p, ev.timestamp_str, sizeof(ev.timestamp_str));
            p += 7; remaining -= 7;
            break;
        }

        /* ── Double-point with CP56Time2a ─────────────── */
        case TI_M_DP_TB_1: {
            if (remaining < 8) goto done;
            uint8_t diq = *p++;  remaining--;
            uint8_t dpi = diq & 0x03;
            const char *dpi_str[] = {"Indet/0","OFF","ON","Indet/3"};
            decode_quality(diq & 0xF0, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%s", dpi_str[dpi]);
            decode_cp56(p, ev.timestamp_str, sizeof(ev.timestamp_str));
            p += 7; remaining -= 7;
            break;
        }

        /* ── ME_TD / ME_TE / ME_TF (with time) ───────── */
        case TI_M_ME_TD_1: {
            if (remaining < 10) goto done;
            int16_t raw = (int16_t)((uint16_t)p[0] | ((uint16_t)p[1]<<8));
            uint8_t qds = p[2];
            float val = raw / 32767.0f;
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%.5f (raw %d)", val, raw);
            decode_cp56(p+3, ev.timestamp_str, sizeof(ev.timestamp_str));
            p += 10; remaining -= 10;
            break;
        }
        case TI_M_ME_TE_1: {
            if (remaining < 10) goto done;
            int16_t raw = (int16_t)((uint16_t)p[0] | ((uint16_t)p[1]<<8));
            uint8_t qds = p[2];
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%d", (int)raw);
            decode_cp56(p+3, ev.timestamp_str, sizeof(ev.timestamp_str));
            p += 10; remaining -= 10;
            break;
        }
        case TI_M_ME_TF_1: {
            if (remaining < 12) goto done;
            float val;
            memcpy(&val, p, 4);
            uint8_t qds = p[4];
            decode_quality(qds, ev.quality_str, sizeof(ev.quality_str));
            snprintf(ev.value_str, sizeof(ev.value_str), "%.6g", (double)val);
            decode_cp56(p+5, ev.timestamp_str, sizeof(ev.timestamp_str));
            p += 12; remaining -= 12;
            break;
        }

        /* ── End of initialisation ────────────────────── */
        case TI_M_EI_NA_1: {
            if (remaining < 1) goto done;
            uint8_t coi = *p++;  remaining--;
            snprintf(ev.value_str, sizeof(ev.value_str), "COI=0x%02X", coi);
            break;
        }

        /* ── Command confirmations (echo back) ────────── */
        case TI_C_IC_NA_1: {
            if (remaining < 1) goto done;
            uint8_t qoi = *p++;  remaining--;
            snprintf(ev.value_str, sizeof(ev.value_str), "QOI=%u", qoi);
            break;
        }
        case TI_C_DC_NA_1:
        case TI_C_DC_TA_1: {
            if (remaining < 1) goto done;
            uint8_t dco = *p++;
            if (type_id == TI_C_DC_TA_1 && remaining >= 8) {
                decode_cp56(p, ev.timestamp_str, sizeof(ev.timestamp_str));
                p += 7; remaining -= 7;
            }
            p++; remaining--;
            const char *dcs_str[] = {"NotPerm0","OFF","ON","NotPerm3"};
            snprintf(ev.value_str, sizeof(ev.value_str), "%s S/E=%d",
                     dcs_str[dco & 0x03], (dco >> 7) & 1);
            break;
        }

        default: {
            /* Unknown type: show raw bytes */
            int show = remaining < 8 ? remaining : 8;
            char *vp = ev.value_str;
            int   vr = sizeof(ev.value_str);
            for (int b = 0; b < show; b++) {
                int w = snprintf(vp, vr, "%02X ", p[b]);
                vp += w; vr -= w;
            }
            p += remaining; remaining = 0;
            break;
        }
        }

        log_event(m, &ev);
        continue;
done:
        break;
    }
    (void)sq;
}

/* ────────────────────────────────────────────────────────────────────── */
/* Frame receiver / dispatcher                                            */
/* ────────────────────────────────────────────────────────────────────── */

static int process_frame(iec104_master_t *m, const uint8_t *buf, int len)
{
    if (len < 6) return -1;
    /* buf[0] = START_BYTE, buf[1] = length of APDU (= total - 2) */

    uint8_t c0 = buf[2];
    uint8_t c1 = buf[3];
    uint8_t c2 = buf[4];
    uint8_t c3 = buf[5];

    m->frames_rx++;
    m->t3_last_rx = time(NULL);

    /* ── U-frame ─────────────────────────────────────── */
    if ((c0 & 0x03) == 0x03) {
        m->u_frames_rx++;
        switch (c0) {
        case U_STARTDT_CON:
            if (m->state == STATE_CONNECTING || m->state == STATE_CONNECTED) {
                m->state = STATE_STARTED;
            }
            break;
        case U_STOPDT_CON:
            m->state = STATE_CONNECTED;
            break;
        case U_TESTFR_ACT:
            send_u_frame(m, U_TESTFR_CON);
            break;
        case U_TESTFR_CON:
            /* nothing special */
            break;
        default:
            break;
        }
        return 0;
    }

    /* ── S-frame ─────────────────────────────────────── */
    if ((c0 & 0x01) == 0x01) {
        m->s_frames_rx++;
        uint16_t ack = ((uint16_t)c2 | ((uint16_t)c3 << 8)) >> 1;
        m->ack_sn = ack;
        return 0;
    }

    /* ── I-frame ─────────────────────────────────────── */
    m->i_frames_rx++;

    /* extract recv SN from our perspective → ack from remote */
    uint16_t remote_ack = ((uint16_t)c2 | ((uint16_t)c3 << 8)) >> 1;
    m->ack_sn = remote_ack;

    /* extract send SN of peer */
    uint16_t peer_sn = ((uint16_t)c0 | ((uint16_t)c1 << 8)) >> 1;
    m->recv_sn = (peer_sn + 1) & 0x7FFF;

    m->unacked_recv++;
    if (m->unacked_recv >= m->w) {
        send_s_frame(m);
    }

    /* ASDU starts at offset 6 */
    int asdu_len = len - 6;
    if (asdu_len > 0) {
        parse_asdu(m, buf + 6, asdu_len, buf, len);
    }

    return 0;
}

/* ────────────────────────────────────────────────────────────────────── */
/* Poll (non-blocking read)                                               */
/* ────────────────────────────────────────────────────────────────────── */

/* Static receive buffer – grows one complete APDU at a time */
#define RXBUF_SIZE 4096
static uint8_t rxbuf[RXBUF_SIZE];
static int     rxbuf_len = 0;

int iec104_poll(iec104_master_t *m)
{
    if (m->sock < 0) return -1;

    /* check connect completion */
    if (m->state == STATE_CONNECTING) {
        fd_set wfds;
        struct timeval tv = {0, 0};
        FD_ZERO(&wfds);
        FD_SET(m->sock, &wfds);
        if (select(m->sock + 1, NULL, &wfds, NULL, &tv) > 0) {
            int err = 0;
            socklen_t len = sizeof(err);
            getsockopt(m->sock, SOL_SOCKET, SO_ERROR, &err, &len);
            if (err == 0) {
                m->state = STATE_CONNECTED;
                /* auto STARTDT */
                m->t1_start = time(NULL);
                send_u_frame(m, U_STARTDT_ACT);
            } else {
                m->state = STATE_ERROR;
                return -1;
            }
        }
        return 0;
    }

    /* read available data */
    int n = read(m->sock, rxbuf + rxbuf_len, RXBUF_SIZE - rxbuf_len);
    if (n < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) return 0;
        m->state = STATE_ERROR;
        return -1;
    }
    if (n == 0) {
        /* peer closed */
        m->state = STATE_DISCONNECTED;
        return -1;
    }
    rxbuf_len += n;

    /* parse complete APDUs */
    while (rxbuf_len >= 2) {
        if (rxbuf[0] != START_BYTE) {
            /* sync error – search for next start byte */
            uint8_t *sp = memchr(rxbuf + 1, START_BYTE, rxbuf_len - 1);
            if (!sp) { rxbuf_len = 0; break; }
            int skip = sp - rxbuf;
            memmove(rxbuf, sp, rxbuf_len - skip);
            rxbuf_len -= skip;
            continue;
        }
        int apdu_len = rxbuf[1] + 2;   /* length field + start + length bytes */
        if (rxbuf_len < apdu_len) break; /* wait for more data */

        process_frame(m, rxbuf, apdu_len);

        memmove(rxbuf, rxbuf + apdu_len, rxbuf_len - apdu_len);
        rxbuf_len -= apdu_len;
    }
    return 0;
}

/* ────────────────────────────────────────────────────────────────────── */
/* Timer tick (call every ~100-500ms)                                     */
/* ────────────────────────────────────────────────────────────────────── */

void iec104_tick(iec104_master_t *m)
{
    if (m->state == STATE_DISCONNECTED || m->state == STATE_ERROR) return;
    time_t now = time(NULL);

    /* T3: send TESTFR_ACT if no frame received for t3 seconds */
    if (m->state == STATE_STARTED) {
        if (now - m->t3_last_rx >= m->t3_seconds) {
            send_u_frame(m, U_TESTFR_ACT);
            m->t3_last_rx = now;
        }
    }

    /* T2: send S-frame ack if we have unacked received I-frames */
    if (m->unacked_recv > 0 && now - m->t3_last_rx >= m->t2_seconds) {
        send_s_frame(m);
    }
}
