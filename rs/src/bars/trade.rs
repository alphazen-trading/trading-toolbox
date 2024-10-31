use chrono::{DateTime, TimeZone, Utc};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use rust_decimal::Decimal;

use crate::sdk::enums::Side; // Replace EnumName1, EnumName2 with actual enums
use rust_decimal::prelude::FromPrimitive; // Import the entire enums module

// Structure representing a Candlestick Bar
#[derive(Debug, Clone)]
#[pyclass(get_all)]
pub struct Trade {
    pub symbol: String,
    pub timestamp_ms: i64,
    pub time: DateTime<Utc>,
    pub price: Decimal,
    pub size: Decimal,
    pub side: Side,
}

#[pymethods]
impl Trade {
    #[new]
    fn new(symbol: String, timestamp_ms: i64, price: f64, size: f64, side: Side) -> PyResult<Self> {
        let time = Utc.timestamp_opt(timestamp_ms / 1000 as i64, 0).unwrap();

        // Convert the f64 values to Decimal
        let price =
            Decimal::from_f64(price).ok_or_else(|| PyValueError::new_err("Invalid open value"))?;
        let size =
            Decimal::from_f64(size).ok_or_else(|| PyValueError::new_err("Invalid high value"))?;

        Ok(Trade {
            symbol,
            timestamp_ms,
            time,
            price,
            size,
            side,
        })
    }
}
