#ifndef IEC104_H
#define IEC104_H

#include <stdint.h>
#include <time.h>

/* ─── APCI Constants ─────────────────────────────────────────────────── */
#define START_BYTE          0x68
#define APCI_LEN            6
#define MAX_APDU_LEN        255
#define MAX_ASDU_LEN        249

/* ─── Frame types ────────────────────────────────────────────────────── */
#define FRAME_I             0   /* bit0=0 */
#define FRAME_S             1   /* bit0=1, bit1=0 */
#define FRAME_U             3   /* bit0=1, bit1=1 */

/* U-frame control field function codes (byte 0, bits 2-7) */
#define U_STARTDT_ACT       0x07  /* 00000111 */
#define U_STARTDT_CON       0x0B  /* 00001011 */
#define U_STOPDT_ACT        0x13  /* 00010011 */
#define U_STOPDT_CON        0x23  /* 00100011 */
#define U_TESTFR_ACT        0x43  /* 01000011 */
#define U_TESTFR_CON        0x83  /* 10000011 */

/* ─── Type Identifiers ───────────────────────────────────────────────── */
#define TI_M_SP_NA_1        1    /* Single-point info */
#define TI_M_DP_NA_1        3    /* Double-point info */
#define TI_M_ST_NA_1        5    /* Step position */
#define TI_M_BO_NA_1        7    /* Bitstring 32bit */
#define TI_M_ME_NA_1        9    /* Measured normalised */
#define TI_M_ME_NB_1        11   /* Measured scaled */
#define TI_M_ME_NC_1        13   /* Measured short float */
#define TI_M_IT_NA_1        15   /* Integrated totals */
#define TI_M_SP_TB_1        30   /* Single-point with CP56Time2a */
#define TI_M_DP_TB_1        31   /* Double-point with CP56Time2a */
#define TI_M_ME_TD_1        34   /* Measured normalised with time */
#define TI_M_ME_TE_1        35   /* Measured scaled with time */
#define TI_M_ME_TF_1        36   /* Short float with time */
#define TI_C_SC_NA_1        45   /* Single command */
#define TI_C_DC_NA_1        46   /* Double command */
#define TI_C_RC_NA_1        47   /* Regulating step command */
#define TI_C_SC_TA_1        58   /* Single command with time */
#define TI_C_DC_TA_1        59   /* Double command with time */
#define TI_C_IC_NA_1        100  /* General interrogation */
#define TI_C_CI_NA_1        101  /* Counter interrogation */
#define TI_M_EI_NA_1        70   /* End of initialisation */

/* ─── Cause of Transmission ──────────────────────────────────────────── */
#define COT_PERIODIC        1
#define COT_BACKGROUND      2
#define COT_SPONTANEOUS     3
#define COT_INITIALIZED     4
#define COT_REQUEST         5
#define COT_ACTIVATION      6
#define COT_ACTCON          7
#define COT_DEACTIVATION    8
#define COT_DEACTCON        9
#define COT_ACTTERM         10
#define COT_RETREM          11
#define COT_RETLOC          12
#define COT_FILE            13
#define COT_INROGEN         20  /* interrogation general */
#define COT_INRO1           21
#define COT_REQCOGEN        37  /* counter request general */
#define COT_UNKNOWN_TYPE    44
#define COT_UNKNOWN_COT     45
#define COT_UNKNOWN_CA      46
#define COT_UNKNOWN_IOA     47

/* ─── Double command values ──────────────────────────────────────────── */
#define DCS_NOT_PERMITTED_0 0
#define DCS_OFF             1
#define DCS_ON              2
#define DCS_NOT_PERMITTED_3 3

/* ─── Quality descriptor bits ────────────────────────────────────────── */
#define QDS_OV   0x01   /* overflow */
#define QDS_BL   0x10   /* blocked */
#define QDS_SB   0x20   /* substituted */
#define QDS_NT   0x40   /* not topical */
#define QDS_IV   0x80   /* invalid */

/* ─── Qualifier of interrogation ─────────────────────────────────────── */
#define QOI_GENERAL         20

/* ─── Structures ─────────────────────────────────────────────────────── */
typedef struct {
    uint8_t  start;         /* 0x68 */
    uint8_t  length;        /* APDU length */
    uint8_t  ctrl[4];       /* control fields */
} __attribute__((packed)) apci_t;

typedef struct {
    uint8_t  type_id;
    uint8_t  vsq;           /* variable structure qualifier */
    uint8_t  cot_low;       /* COT low byte (includes P/N and T bits) */
    uint8_t  cot_high;      /* originator address */
    uint8_t  ca_low;        /* common address low */
    uint8_t  ca_high;       /* common address high */
} __attribute__((packed)) asdu_header_t;

/* CP56Time2a (7 bytes) */
typedef struct {
    uint16_t ms;            /* milliseconds */
    uint8_t  min;           /* minutes (0-59), bit6=RES, bit7=IV */
    uint8_t  hour;          /* hours (0-23), bits 5-7 = RES/SU */
    uint8_t  dom;           /* day of month (1-31), day of week bits 5-7 */
    uint8_t  month;         /* month (1-12) */
    uint8_t  year;          /* year (0-99) */
} __attribute__((packed)) cp56time2a_t;

/* ─── Connection state ───────────────────────────────────────────────── */
typedef enum {
    STATE_DISCONNECTED = 0,
    STATE_CONNECTING,
    STATE_CONNECTED,        /* TCP up, STARTDT not yet sent */
    STATE_STARTED,          /* STARTDT_CON received, I-frames allowed */
    STATE_STOPPING,
    STATE_ERROR
} conn_state_t;

/* ─── Event record (for the event log) ──────────────────────────────── */
#define MAX_EVENTS          500
#define MAX_EVENT_STR       256

typedef struct {
    time_t   recv_time;
    uint8_t  type_id;
    uint8_t  cot;
    uint16_t ca;
    uint32_t ioa;
    char     value_str[128];
    char     quality_str[64];
    char     timestamp_str[64];  /* CP56Time2a if present */
    uint8_t  raw[MAX_APDU_LEN];
    int      raw_len;
} event_record_t;

/* ─── Master context ─────────────────────────────────────────────────── */
typedef struct {
    int         sock;
    conn_state_t state;

    char        host[128];
    int         port;
    uint16_t    common_addr;    /* CA to use for commands */

    /* I-frame sequence numbers */
    uint16_t    send_sn;        /* VS - variable send sequence number */
    uint16_t    recv_sn;        /* VR - variable receive sequence number */
    uint16_t    ack_sn;         /* last acknowledged send SN */

    /* Timers */
    time_t      t1_start;       /* STARTDT timeout / I-frame ack timeout */
    time_t      t3_last_rx;     /* last received frame time (for TESTFR) */
    int         t1_seconds;     /* default 15 */
    int         t2_seconds;     /* default 10 – S-frame ack timeout */
    int         t3_seconds;     /* default 20 – TESTFR timeout */

    /* w parameter – max un-acked I-frames before sending S */
    int         w;              /* default 8 */
    int         unacked_recv;   /* frames received since last S-frame */

    /* Event log */
    event_record_t events[MAX_EVENTS];
    int            event_count;
    int            event_head;  /* ring-buffer head */

    /* Stats */
    uint64_t    frames_tx;
    uint64_t    frames_rx;
    uint64_t    i_frames_rx;
    uint64_t    s_frames_rx;
    uint64_t    u_frames_rx;
} iec104_master_t;

/* ─── API ────────────────────────────────────────────────────────────── */
void iec104_init(iec104_master_t *m, const char *host, int port, uint16_t ca);
int  iec104_connect(iec104_master_t *m);
void iec104_disconnect(iec104_master_t *m);
int  iec104_start_dt(iec104_master_t *m);
int  iec104_send_gi(iec104_master_t *m);
int  iec104_send_double_cmd(iec104_master_t *m, uint32_t ioa, uint8_t dcs, int select);
int  iec104_poll(iec104_master_t *m);   /* non-blocking, call in loop */
void iec104_tick(iec104_master_t *m);   /* call every ~100ms for timers */

const char *iec104_type_name(uint8_t type_id);
const char *iec104_cot_name(uint8_t cot);
const char *iec104_state_name(conn_state_t s);

#endif /* IEC104_H */
