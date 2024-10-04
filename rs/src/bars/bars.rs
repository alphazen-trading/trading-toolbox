use super::ohlcv::OHLCV;
use arrow::array::{Float64Array, Int64Array, StringArray, TimestampMillisecondArray};
use arrow::datatypes::{DataType, Field, Schema, TimeUnit};
use parquet::arrow::arrow_writer::ArrowWriter;
use parquet::file::properties::WriterProperties;
use pyo3::prelude::*;
use rust_decimal::prelude::ToPrimitive;
use std::fs::File;
use std::sync::Arc;

/// Represents a collection of OHLCV (Open, High, Low, Close, Volume) data
/// for traditional and Heikin-Ashi bars.
///
/// The `Bars` struct contains two vectors: one for standard OHLCV data and
/// another for Heikin-Ashi bar data. This struct provides an organized way
/// to manage and manipulate historical price data, facilitating
/// various analytical and trading strategies.
///
/// Attributes:
///     ohlcvs (Vec<OHLCV>): A vector containing the standard OHLCV data.
///     ha_bars (Vec<OHLCV>): A vector containing Heikin-Ashi OHLCV data.
#[pyclass(get_all)]
pub struct Bars {
    ohlcvs: Vec<OHLCV>,
    ha_bars: Vec<OHLCV>,
}

#[pymethods]
impl Bars {
    #[new]
    fn new() -> PyResult<Self> {
        Ok(Bars {
            ohlcvs: Vec::new(),
            ha_bars: Vec::new(),
        })
    }

    fn add_ohlcv(&mut self, ohlcv: OHLCV) -> PyResult<()> {
        self.ohlcvs.push(ohlcv);
        Ok(())
    }

    fn to_parquet(&self) -> PyResult<()> {
        Ok(())
    }

    fn write_ohlcv_to_parquet(&self, file_path: &str) -> PyResult<()> {
        // Define the schema for OHLCV
        let schema = Arc::new(Schema::new(vec![
            Field::new("symbol", DataType::Utf8, false),
            Field::new("timestamp_ms", DataType::Int64, false),
            Field::new(
                "time",
                DataType::Timestamp(TimeUnit::Millisecond, None),
                false,
            ),
            Field::new("open", DataType::Float64, false),
            Field::new("high", DataType::Float64, false),
            Field::new("low", DataType::Float64, false),
            Field::new("close", DataType::Float64, false),
            Field::new("volume", DataType::Float64, false),
        ]));

        // Convert OHLCV data into Arrow arrays
        let ohlcv_data = &self.ohlcvs.clone();
        let symbols: Vec<&str> = ohlcv_data.iter().map(|o| o.symbol.as_str()).collect();
        let timestamps: Vec<i64> = ohlcv_data.iter().map(|o| o.timestamp_ms).collect();
        let times: Vec<i64> = ohlcv_data
            .iter()
            .map(|o| o.time.timestamp_millis())
            .collect();
        let opens: Vec<f64> = ohlcv_data
            .iter()
            .map(|o| o.open.to_f64().unwrap())
            .collect();
        let highs: Vec<f64> = ohlcv_data
            .iter()
            .map(|o| o.high.to_f64().unwrap())
            .collect();
        let lows: Vec<f64> = ohlcv_data.iter().map(|o| o.low.to_f64().unwrap()).collect();
        let closes: Vec<f64> = ohlcv_data
            .iter()
            .map(|o| o.close.to_f64().unwrap())
            .collect();
        let volumes: Vec<f64> = ohlcv_data
            .iter()
            .map(|o| o.volume.to_f64().unwrap())
            .collect();

        // Create Arrow arrays
        let symbol_array = StringArray::from(symbols);
        let timestamp_array = Int64Array::from(timestamps);
        let time_array = TimestampMillisecondArray::from(times);
        let open_array = Float64Array::from(opens);
        let high_array = Float64Array::from(highs);
        let low_array = Float64Array::from(lows);
        let close_array = Float64Array::from(closes);
        let volume_array = Float64Array::from(volumes);

        // Create a record batch (collection of columns) from arrays
        let batch = arrow::record_batch::RecordBatch::try_new(
            schema.clone(),
            vec![
                Arc::new(symbol_array),
                Arc::new(timestamp_array),
                Arc::new(time_array),
                Arc::new(open_array),
                Arc::new(high_array),
                Arc::new(low_array),
                Arc::new(close_array),
                Arc::new(volume_array),
            ],
        )
        .unwrap();

        // Create a file to write the Parquet data to
        let file = File::create(file_path).unwrap();

        // Create a Parquet writer
        let writer_props = WriterProperties::builder().build();
        let mut writer = ArrowWriter::try_new(file, schema.clone(), Some(writer_props)).unwrap();

        // Write the record batch to the Parquet file
        writer.write(&batch).unwrap();

        // Finalize and close the writer
        writer.close().unwrap();

        Ok(())
    }
}
