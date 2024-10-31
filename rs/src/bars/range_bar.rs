use super::trade::Trade;
use chrono::{DateTime, Utc};
use pyo3::prelude::*;
use rust_decimal::prelude::FromPrimitive;
use rust_decimal::Decimal;

// Structure representing a Range Bar
#[derive(Debug, Clone)]
#[pyclass(get_all, set_all)]
pub struct RangeBar {
    pub open: Decimal,
    pub high: Decimal,
    pub low: Decimal,
    pub close: Decimal,
    pub volume: Decimal,
    pub start_time: DateTime<Utc>,
    pub end_time: DateTime<Utc>,
}

#[pymethods]
impl RangeBar {
    #[new]
    pub fn new(first_trade: &Trade) -> PyResult<Self> {
        Ok(RangeBar {
            open: first_trade.price,
            high: first_trade.price,
            low: first_trade.price,
            close: first_trade.price,
            volume: first_trade.size,
            start_time: first_trade.time,
            end_time: first_trade.time,
        })
    }

    // Update the range bar with a new trade
    pub fn update(&mut self, trade: &Trade) {
        if trade.price > self.high {
            self.high = trade.price;
        }
        if trade.price < self.low {
            self.low = trade.price;
        }
        self.close = trade.price;
        self.volume += trade.size;
        self.end_time = trade.time;
    }

    pub fn exceeds_threshold(
        &self,
        trade: &Trade,
        threshold: Decimal,
        is_percentage: bool,
    ) -> bool {
        if is_percentage {
            let price_diff = (trade.price - self.open).abs();
            let percentage_movement = price_diff / self.open * Decimal::from_f64(100.0).unwrap();
            percentage_movement >= threshold // Return bool
        } else {
            (trade.price - self.open).abs() >= threshold // Return bool
        }
    }
}
