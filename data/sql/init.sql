-- Bank of Canada MLOps Platform - Database Initialization
-- This script creates the initial database structure and sample data

-- Create the main database if it doesn't exist
-- Note: This runs automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas for organization
CREATE SCHEMA IF NOT EXISTS economic_data;
CREATE SCHEMA IF NOT EXISTS ml_models;
CREATE SCHEMA IF NOT EXISTS system_monitoring;
CREATE SCHEMA IF NOT EXISTS user_management;

-- Economic indicators reference data
INSERT INTO economic_indicators (code, name, description, unit, frequency, category, source) VALUES
('CPIXCORE', 'Core Consumer Price Index', 'CPI excluding food and energy', 'Index', 'monthly', 'inflation', 'Bank of Canada'),
('CPIX', 'Consumer Price Index', 'All-items CPI', 'Index', 'monthly', 'inflation', 'Bank of Canada'),
('UNRATE', 'Unemployment Rate', 'Unemployment rate, seasonally adjusted', '%', 'monthly', 'employment', 'Statistics Canada'),
('GDP', 'Gross Domestic Product', 'Real GDP at basic prices', 'CAD Million', 'quarterly', 'gdp', 'Statistics Canada'),
('POLRATE', 'Policy Interest Rate', 'Bank of Canada overnight rate', '%', 'daily', 'interest_rates', 'Bank of Canada'),
('FXUSDCAD', 'USD/CAD Exchange Rate', 'US Dollar to Canadian Dollar exchange rate', 'Rate', 'daily', 'exchange_rates', 'Bank of Canada'),
('FXEURCAD', 'EUR/CAD Exchange Rate', 'Euro to Canadian Dollar exchange rate', 'Rate', 'daily', 'exchange_rates', 'Bank of Canada'),
('NHPI', 'New Housing Price Index', 'New housing price index', 'Index', 'monthly', 'housing', 'Statistics Canada')
ON CONFLICT (code) DO NOTHING;

-- Default user roles
INSERT INTO roles (name, description, level, permissions) VALUES
('admin', 'System Administrator', 4, '{"all": true}'),
('economist', 'Senior Economist', 3, '{"read": true, "write": true, "model_deploy": true}'),
('analyst', 'Economic Analyst', 2, '{"read": true, "write": false, "model_view": true}'),
('viewer', 'Dashboard Viewer', 1, '{"read": true}')
ON CONFLICT (name) DO NOTHING;

-- Create default admin user (password: admin123)
-- Note: In production, this should be changed immediately
INSERT INTO users (
    username, 
    email, 
    hashed_password, 
    first_name, 
    last_name, 
    role_id, 
    is_active, 
    is_verified,
    created_by
) VALUES (
    'admin',
    'admin@bankcanada.ca',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/GyqVLqbB5bQCdO5.6', -- hashed "admin123"
    'System',
    'Administrator',
    (SELECT id FROM roles WHERE name = 'admin'),
    true,
    true,
    'system'
)
ON CONFLICT (username) DO NOTHING;

-- Sample economic events for demonstration
INSERT INTO economic_events (name, description, event_date, event_type, significance_level, source) VALUES
('Bank of Canada Rate Decision', 'Overnight rate maintained at 5.00%', CURRENT_DATE - INTERVAL '30 days', 'rate_decision', 'high', 'Bank of Canada'),
('Inflation Report Released', 'Q4 2023 Monetary Policy Report', CURRENT_DATE - INTERVAL '60 days', 'report_release', 'medium', 'Bank of Canada'),
('Employment Data Release', 'Monthly labour force statistics', CURRENT_DATE - INTERVAL '15 days', 'data_release', 'medium', 'Statistics Canada')
ON CONFLICT DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_economic_data_points_date ON economic_data_points (date DESC);
CREATE INDEX IF NOT EXISTS idx_economic_data_points_indicator_date ON economic_data_points (indicator_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_economic_forecasts_target_date ON economic_forecasts (target_date DESC);
CREATE INDEX IF NOT EXISTS idx_ml_runs_start_time ON ml_runs (start_time DESC);
CREATE INDEX IF NOT EXISTS idx_user_audit_logs_timestamp ON user_audit_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics (timestamp DESC);

-- Create materialized view for dashboard summary
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_summary AS
SELECT 
    ei.code,
    ei.name,
    ei.category,
    edp.value as latest_value,
    edp.date as latest_date,
    lag(edp.value) OVER (PARTITION BY ei.id ORDER BY edp.date) as previous_value,
    edp.quality_score
FROM economic_indicators ei
LEFT JOIN LATERAL (
    SELECT value, date, quality_score
    FROM economic_data_points 
    WHERE indicator_id = ei.id 
    ORDER BY date DESC 
    LIMIT 2
) edp ON true
WHERE ei.is_active = true;

-- Create refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_dashboard_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW dashboard_summary;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT USAGE ON SCHEMA economic_data TO admin;
GRANT USAGE ON SCHEMA ml_models TO admin;
GRANT USAGE ON SCHEMA system_monitoring TO admin;
GRANT USAGE ON SCHEMA user_management TO admin;

-- Log successful initialization
INSERT INTO user_audit_logs (user_id, action, resource_type, timestamp, status, ip_address) VALUES
(1, 'database_initialization', 'system', NOW(), 'success', '127.0.0.1');

-- Display completion message
DO $$
BEGIN
    RAISE NOTICE 'Bank of Canada MLOps Database initialized successfully!';
    RAISE NOTICE 'Default admin user: admin@bankcanada.ca / admin123';
    RAISE NOTICE 'Created % economic indicators', (SELECT COUNT(*) FROM economic_indicators);
    RAISE NOTICE 'Created % user roles', (SELECT COUNT(*) FROM roles);
END $$;
