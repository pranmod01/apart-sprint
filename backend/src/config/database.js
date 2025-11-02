import pg from 'pg';
import dotenv from 'dotenv';
import { logger } from './logger.js';

dotenv.config();

const { Pool } = pg;

// PostgreSQL connection pool
export const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'ai_terrain_db',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD,
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Test database connection
pool.on('connect', () => {
  logger.info('✓ Database connected');
});

pool.on('error', (err) => {
  logger.error('Unexpected database error:', err);
  process.exit(-1);
});

// Query helper function
export const query = async (text, params) => {
  const start = Date.now();
  try {
    const res = await pool.query(text, params);
    const duration = Date.now() - start;
    logger.debug(`Executed query: ${text} | Duration: ${duration}ms`);
    return res;
  } catch (error) {
    logger.error(`Query error: ${error.message}`);
    throw error;
  }
};

// Initialize database schema
export const initializeDatabase = async () => {
  try {
    // Create tables for benchmarks
    await query(`
      CREATE TABLE IF NOT EXISTS capabilities (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        category VARCHAR(100),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    await query(`
      CREATE TABLE IF NOT EXISTS benchmarks (
        id SERIAL PRIMARY KEY,
        capability_id INTEGER REFERENCES capabilities(id),
        model_name VARCHAR(255) NOT NULL,
        score DECIMAL(5, 2) NOT NULL,
        benchmark_name VARCHAR(255),
        date DATE NOT NULL,
        source VARCHAR(50) CHECK (source IN ('epoch_ai', 'papers_with_code', 'manual')),
        metadata JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Create indexes for faster queries
    await query(`
      CREATE INDEX IF NOT EXISTS idx_benchmarks_capability
      ON benchmarks(capability_id);
    `);

    await query(`
      CREATE INDEX IF NOT EXISTS idx_benchmarks_date
      ON benchmarks(date DESC);
    `);

    await query(`
      CREATE INDEX IF NOT EXISTS idx_benchmarks_model
      ON benchmarks(model_name);
    `);

    // Create table for anomalies/alerts
    await query(`
      CREATE TABLE IF NOT EXISTS anomalies (
        id SERIAL PRIMARY KEY,
        capability_id INTEGER REFERENCES capabilities(id),
        anomaly_type VARCHAR(50) CHECK (anomaly_type IN ('jump', 'convergence', 'sinkhole', 'breakthrough')),
        severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
        description TEXT,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB,
        resolved BOOLEAN DEFAULT FALSE
      );
    `);

    // Create table for forecasts
    await query(`
      CREATE TABLE IF NOT EXISTS forecasts (
        id SERIAL PRIMARY KEY,
        capability_id INTEGER REFERENCES capabilities(id),
        threshold INTEGER NOT NULL,
        predicted_date DATE,
        confidence_interval JSONB,
        model_type VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB
      );
    `);

    // Create table for sinkholes
    await query(`
      CREATE TABLE IF NOT EXISTS sinkholes (
        id SERIAL PRIMARY KEY,
        task_name VARCHAR(255) NOT NULL,
        description TEXT,
        difficulty_expected VARCHAR(20),
        difficulty_actual VARCHAR(20),
        failure_rate DECIMAL(5, 2),
        examples JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    logger.info('✓ Database schema initialized');
  } catch (error) {
    logger.error('Database initialization error:', error);
    throw error;
  }
};

export default { pool, query, initializeDatabase };
