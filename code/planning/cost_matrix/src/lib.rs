use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn calculate_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    // Haversine formula implementation for distance calculation
    const R: f64 = 6371.0; // Earth radius in kilometers
    let d_lat = (lat2 - lat1).to_radians();
    let d_lon = (lon2 - lon1).to_radians();
    let a = (d_lat / 2.0).sin() * (d_lat / 2.0).sin()
        + lat1.to_radians().cos() * lat2.to_radians().cos() * (d_lon / 2.0).sin() * (d_lon / 2.0).sin();
    let c = 2.0 * a.sqrt().atan2((1.0 - a).sqrt());
    R * c
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_cost_matrix(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_distance, m)?)?;
    Ok(())
}