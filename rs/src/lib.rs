mod bars;
use bars::bars::Bars;
use bars::ohlcv::OHLCV;
use pyo3::prelude::*;

#[pymodule]
fn rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OHLCV>()?;
    m.add_class::<Bars>()?;

    // m.add_function(wrap_pyfunction!(cross_above, m)?)?;
    // m.add_function(wrap_pyfunction!(cross_below, m)?)?;
    Ok(())
}
