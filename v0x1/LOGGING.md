# Logging Configuration for Production

## Log Files Structure

The application creates the following log files in the `logs/` directory:

### 1. `daemon.log` - Main Application Log
- **Rotation**: Daily at midnight
- **Retention**: 30 days
- **Level**: DEBUG and above
- **Contains**: All application events, task processing, general operations

### 2. `daemon_errors.log` - Error Log
- **Rotation**: Size-based (10MB per file)
- **Retention**: 5 files
- **Level**: ERROR and above only
- **Contains**: Errors, exceptions, critical failures

### 3. `websocket.log` - WebSocket Communications
- **Rotation**: Daily at midnight
- **Retention**: 7 days
- **Level**: DEBUG and above
- **Contains**: WebSocket connections, client events, message broadcasting

### 4. `task_processing.log` - Task Execution
- **Rotation**: Daily at midnight
- **Retention**: 14 days
- **Level**: DEBUG and above
- **Contains**: AI task decomposition, command execution, task tree building

### 5. `taskagent.log` - Legacy Log (Backward Compatibility)
- **Rotation**: Manual
- **Retention**: Manual
- **Level**: All levels
- **Contains**: Legacy format messages for compatibility

## Log Levels

### DEBUG
- Detailed diagnostic information
- WebSocket message details
- Task tree state changes
- API response parsing

### INFO
- General application flow
- Task execution steps
- Client connections
- Successful operations

### WARNING
- Recoverable errors
- Missing optional configuration
- Performance issues

### ERROR
- API failures
- WebSocket connection errors
- Task execution failures
- JSON parsing errors

### CRITICAL
- Application cannot continue
- Server startup failures
- System-level issues

## Production Deployment

### 1. Log Directory Permissions
```bash
# Ensure log directory has proper permissions
mkdir -p logs
chmod 755 logs
chown daemon:daemon logs
```

### 2. Log Rotation (System Level)
Create `/etc/logrotate.d/taskagent`:
```
/path/to/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### 3. Monitoring and Alerting
- Monitor `daemon_errors.log` for critical errors
- Set up alerts for ERROR level messages
- Monitor disk space for log files
- Watch for rapid log growth indicating issues

### 4. Log Analysis
```bash
# View recent errors
tail -f logs/daemon_errors.log

# Search for specific issues
grep "WebSocket error" logs/websocket.log

# Monitor task execution
tail -f logs/task_processing.log

# View all recent activity
tail -f logs/daemon.log
```

### 5. Environment Variables
```bash
# Set log level for production
export LOG_LEVEL=INFO

# Set log directory
export LOG_DIR=/var/log/taskagent
```

### 6. Systemd Integration
Add to your systemd service file:
```ini
[Unit]
Description=Task Agent Daemon
After=network.target

[Service]
Type=simple
User=daemon
Group=daemon
WorkingDirectory=/opt/taskagent
ExecStart=/usr/bin/python3 0x1daemon.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=taskagent

[Install]
WantedBy=multi-user.target
```

### 7. Log Shipping (Optional)
For centralized logging, consider:
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Fluentd**: Log aggregation
- **Syslog**: Traditional system logging
- **Cloud Services**: AWS CloudWatch, Azure Monitor, etc.

## Security Considerations

### 1. Sensitive Data
- API keys are not logged in production
- User data is sanitized before logging
- Command outputs may contain sensitive information

### 2. Access Control
```bash
# Restrict log file access
chmod 640 logs/*.log
chown daemon:adm logs/*.log
```

### 3. Log Integrity
- Consider log signing for audit trails
- Use append-only log storage
- Regular backup of critical logs

## Performance Impact

### 1. File I/O
- Async logging to reduce blocking
- Buffered writes for better performance
- SSD storage recommended for high-volume logging

### 2. Log Level Management
```python
# Reduce logging in production
logging.getLogger().setLevel(logging.WARNING)

# Or use environment variable
import os
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.getLogger().setLevel(getattr(logging, log_level))
```

### 3. Log Sampling
For very high-volume applications, implement log sampling:
```python
import random

def should_log_debug():
    return random.random() < 0.1  # Log 10% of debug messages
```