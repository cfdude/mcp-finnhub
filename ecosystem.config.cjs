module.exports = {
  apps: [
    {
      name: 'mcp-finnhub',
      script: '/Users/robsherman/Servers/mcp-finnhub/.venv/bin/python',
      args: '-m mcp_finnhub --transport http --host 127.0.0.1 --port 8101',
      cwd: '/Users/robsherman/Servers/mcp-finnhub',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      env: {
        PYTHONUNBUFFERED: '1',
        FINNHUB_API_KEY: 'd4bfdj1r01qnomk4krk0d4bfdj1r01qnomk4krkg',
        FINNHUB_STORAGE_DIR: '/Users/robsherman/Documents/finnhub-data',
        FINNHUB_SAFE_TOKEN_LIMIT: '75000',
        FINNHUB_RATE_LIMIT_RPM: '150',
        FINNHUB_REQUEST_TIMEOUT: '30',
      },
      // Logging
      log_file: './logs/mcp-finnhub.log',
      error_file: './logs/mcp-finnhub-error.log',
      out_file: './logs/mcp-finnhub-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      // Restart behavior
      autorestart: true,
      restart_delay: 4000,
      max_restarts: 10,
      min_uptime: '10s',
      max_memory_restart: '300M',
    }
  ]
};
