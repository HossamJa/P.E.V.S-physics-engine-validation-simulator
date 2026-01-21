from .simulation_result import SimulationResult

def serialize_simulation(result: SimulationResult):
    return {
        "summary": result.summary(),
        "final_state": result.final_state(),
        "timeseries": result.timeseries(),
        "conservation": result.conservation(),
        "engine": result.engine(),
        "environment": result.environment(),
        "accounting": result.accounting(),
        "audit": result.audit(),
        "reports": result.reports(),
        "raw_data": result.raw_data()
    }
