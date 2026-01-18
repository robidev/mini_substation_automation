#include <libiec61850/iec61850_server.h>
#include <libiec61850/iec61850_model.h>
#include <libiec61850/hal_thread.h>

#include "open_server.h"
#include "iec61850_dynamic_model_extensions.h"
#include "iec61850_config_file_parser_extensions.h"
#include "iec61850_model_extensions.h"
#include "inputs_api.h"
#include "timestep_config.h"
#include "config_parser.h"
#include <stdio.h>
#include <string.h>


// SOCKET example code
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <errno.h>
#include <signal.h>

#define BUFFER_SIZE 4096
#define LINE_BUFFER_SIZE 8192

typedef struct {
    int sockfd;
    volatile int *shutdown_flag;
} thread_args_t;

static volatile int shutdown_flag = 0;
// socket example code end

// check ied-name, for config-entry
// connect to socket based on config
// connect cbr callback to xcbr/xswi and io-index based on config
// receive switch-status events, and modify respective stval(ref in config)
// when an operate-signal is send, send set io command over socket, based on config
// receive transformer-data and write it into CTR/VTR elements
//
// possible timestep call from socket to all clients?(to pace and sync the ieds?)
// possible dsp-override: if so, when a dsp-processing call is made, we just provide the rms-value the sine was calced from in the first place
//
//     if cmd[0] == "SET" and len(cmd) == 3:    ch = int(cmd[1]) state_val = cmd[2]
//   elif cmd[0] == "GET" and len(cmd) == 2:  ch = int(cmd[1])
//   elif cmd[0] == "GETDATA":

int init(OpenServerInstance *srv)
{
    IedModel *model;
    IedModel_extensions *model_ex;

    printf(" hw_connector module initialising\n");
    model = srv->Model;
    model_ex = srv->Model_ex;
    
    config_t config;
    
    /* Parse the config file */
    if (config_parse_file("./plugin/hw_connector.config", &config) != 0) {
        printf("ERROR: Failed to parse config file\n");
        return 1;
    }
    
    /* Find a specific device section */
    config_section_t *section = config_find_section(&config, model->name);
    
    if (!section) {
        printf("ERROR: Device '%s' not found in config\n", model->name);
        config_free(&config);
        return 1;
    }

    printf(" Device: %s\n", section->section);
    const char *socket_path = config_get_value(section, "socket");

    /* Iterate through all key-value pairs */
    printf("\n === All settings for %s ===\n", model->name);
    for (int i = 0; i < section->entry_count; i++) {
        printf("  %s = ", section->entries[i].key);
        if (section->entries[i].value_count == 1) {
            printf("%s\n", section->entries[i].values[0]);
        } else {
            printf("[");
            for (int j = 0; j < section->entries[i].value_count; j++) {
                printf("%s%s", section->entries[i].values[j],
                       j < section->entries[i].value_count - 1 ? ", " : "");
            }
            printf("]\n");
        }
    }

    config_free(&config);


    printf("hw_connector module initialised\n");
    return 0; // 0 means success
}



void signal_handler(int signum) {
    shutdown_flag = 1;
}

void *receiver_thread(void *arg) {
    thread_args_t *args = (thread_args_t *)arg;
    int sockfd = args->sockfd;
    char buffer[BUFFER_SIZE];
    char line_buffer[LINE_BUFFER_SIZE] = {0};
    int line_pos = 0;
    
    while (!shutdown_flag) {
        ssize_t n = recv(sockfd, buffer, sizeof(buffer) - 1, 0);
        
        if (n < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                usleep(10000); // 10ms
                continue;
            }
            if (!shutdown_flag) {
                fprintf(stderr, "\n[Receiver error: %s]\n", strerror(errno));
            }
            break;
        }
        
        if (n == 0) {
            printf("\n[Server closed connection]\n");
            shutdown_flag = 1;
            break;
        }
        
        buffer[n] = '\0';
        
        // Add to line buffer and process complete lines
        for (ssize_t i = 0; i < n; i++) {
            if (buffer[i] == '\n') {
                line_buffer[line_pos] = '\0';
                
                // Trim whitespace
                char *line = line_buffer;
                while (*line == ' ' || *line == '\t' || *line == '\r') line++;
                
                if (*line != '\0') {
                    // Check if it's a broadcast event
                    if (strncmp(line, "EVENT ", 6) == 0) {
                        char *event_data = line + 6;
                        printf("\n[BROADCAST] %s\n", event_data);
                    } else {
                        printf("\n[RESPONSE] %s\n", line);
                    }
                    printf("> ");
                    fflush(stdout);
                }
                
                line_pos = 0;
            } else {
                if (line_pos < LINE_BUFFER_SIZE - 1) {
                    line_buffer[line_pos++] = buffer[i];
                }
            }
        }
    }
    
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <unix_socket_path>\n", argv[0]);
        return 1;
    }
    
    const char *sock_path = argv[1];
    
    // Create socket
    int sockfd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }
    
    // Set receive timeout
    struct timeval tv;
    tv.tv_sec = 0;
    tv.tv_usec = 500000; // 500ms
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("setsockopt");
        close(sockfd);
        return 1;
    }
    
    // Connect to Unix socket
    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);
    
    if (connect(sockfd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        fprintf(stderr, "Failed to connect to %s: %s\n", sock_path, strerror(errno));
        close(sockfd);
        return 1;
    }
    
    printf("Connected to %s\n", sock_path);
    printf("\nCommands:\n");
    printf("  SET <channel> <value>    - Set channel state\n");
    printf("  GET <channel>            - Get current event state for channel\n");
    printf("  GETDATA                  - Get current data message\n");
    printf("  quit                     - Exit program\n");
    printf("\nBroadcast events will be displayed automatically as [BROADCAST]\n");
    printf("------------------------------------------------------------\n");
    
    // Set up signal handler for Ctrl+C
    signal(SIGINT, signal_handler);
    
    // Start receiver thread
    pthread_t recv_tid;
    thread_args_t thread_args = {sockfd, &shutdown_flag};
    
    if (pthread_create(&recv_tid, NULL, receiver_thread, &thread_args) != 0) {
        perror("pthread_create");
        close(sockfd);
        return 1;
    }
    
    // Main input loop
    char cmd[1024];
    while (!shutdown_flag) {
        printf("> ");
        fflush(stdout);
        
        if (fgets(cmd, sizeof(cmd), stdin) == NULL) {
            break;
        }
        
        // Remove newline
        size_t len = strlen(cmd);
        if (len > 0 && cmd[len - 1] == '\n') {
            cmd[len - 1] = '\0';
            len--;
        }
        
        // Trim leading/trailing whitespace
        char *trimmed = cmd;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++;
        
        if (*trimmed == '\0') {
            continue;
        }
        
        // Check for quit command
        if (strcasecmp(trimmed, "quit") == 0 || strcasecmp(trimmed, "exit") == 0) {
            break;
        }
        
        // Send command with newline
        char send_buf[1026];
        snprintf(send_buf, sizeof(send_buf), "%s\n", trimmed);
        
        ssize_t sent = send(sockfd, send_buf, strlen(send_buf), 0);
        if (sent < 0) {
            fprintf(stderr, "[Send error: %s]\n", strerror(errno));
            break;
        }
    }
    
    printf("\n[Interrupted]\n");
    shutdown_flag = 1;
    
    // Wait for receiver thread to finish
    pthread_join(recv_tid, NULL);
    
    close(sockfd);
    printf("Disconnected\n");
    
    return 0;
}