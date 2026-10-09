
-- ==========================================
-- FINFLOW - FINANCIAL DATA PIPELINE
-- Database: finflow_db
-- Table: stock_prices
-- ==========================================

CREATE TABLE IF NOT EXISTS stock_prices (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,

    open NUMERIC(12, 4) NOT NULL,
    high NUMERIC(12, 4) NOT NULL,
    low NUMERIC(12, 4) NOT NULL,
    close NUMERIC(12, 4) NOT NULL,

    volume BIGINT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (symbol, date),

    CONSTRAINT chk_stock_prices_positive
        CHECK (
            open > 0 AND
            high > 0 AND
            low > 0 AND
            close > 0
        ),

    CONSTRAINT chk_stock_volume
        CHECK (volume >= 0),

    CONSTRAINT chk_stock_price_range
        CHECK (
            high >= low AND
            open BETWEEN low AND high AND
            close BETWEEN low AND high
        )
);
