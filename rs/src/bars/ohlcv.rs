use chrono::{DateTime, TimeZone, Utc};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use rust_decimal::Decimal;

use rust_decimal::prelude::FromPrimitive;

// Structure representing a Candlestick Bar
#[derive(Debug, Clone)]
#[pyclass(get_all, set_all)]
pub struct OHLCV {
    pub symbol: String,
    pub timestamp_ms: i64,
    pub time: DateTime<Utc>,
    pub open: Decimal,
    pub high: Decimal,
    pub low: Decimal,
    pub close: Decimal,
    pub volume: Decimal,
}

#[pymethods]
impl OHLCV {
    #[new]
    fn new(
        symbol: String,
        timestamp_ms: i64,
        open: f64,
        high: f64,
        low: f64,
        close: f64,
        volume: f64,
    ) -> PyResult<Self> {
        let time = Utc.timestamp_opt(timestamp_ms / 1000 as i64, 0).unwrap();

        // Convert the f64 values to Decimal
        let open =
            Decimal::from_f64(open).ok_or_else(|| PyValueError::new_err("Invalid open value"))?;
        let high =
            Decimal::from_f64(high).ok_or_else(|| PyValueError::new_err("Invalid high value"))?;
        let low =
            Decimal::from_f64(low).ok_or_else(|| PyValueError::new_err("Invalid high value"))?;
        let close =
            Decimal::from_f64(close).ok_or_else(|| PyValueError::new_err("Invalid high value"))?;
        let volume =
            Decimal::from_f64(volume).ok_or_else(|| PyValueError::new_err("Invalid high value"))?;

        Ok(OHLCV {
            symbol,
            timestamp_ms,
            time,
            open,
            high,
            low,
            close,
            volume,
        })
    }
}
