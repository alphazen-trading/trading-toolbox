mod bars;
mod sdk;
use bars::bars::Bars;
use bars::ohlcv::OHLCV;
use bars::trade::Trade;
use pyo3::prelude::*;
use sdk::enums::Side;

#[pymodule]
fn rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OHLCV>()?;
    m.add_class::<Bars>()?;
    m.add_class::<Side>()?;
    m.add_class::<Trade>()?;

    // m.add_function(wrap_pyfunction!(cross_above, m)?)?;
    // m.add_function(wrap_pyfunction!(cross_below, m)?)?;
    Ok(())
}
