# Market Mapper Calculation System Design

## Overview
This document outlines the design of the calculation system used in Market Mapper. The system is built around nodes containing rows, where each row can have its own calculation logic and dependencies.

## Core Concepts

### 1. Node Structure
A node represents a logical grouping of related calculations. For example, a "Total Revenue" node might contain:
- Volume Sold
- Average Price
- Revenue

### 2. Row Structure
Each row within a node contains:
```
{
    metadata: {
        index: int,          # Determines calculation order
        step: int,           # Sub-ordering within same index
        name: str,           # Row name
        description: str     # Optional description
    },
    local_variables: {       # Variables specific to this calculation
        variable_name: {
            type: str,       # number, date, array, timeSeries
            value: any,
            validation: {    # Optional validation rules
                min: float,
                max: float,
                format: str
            },
            metadata: {      # Additional information
                unit: str,
                display_format: str
            }
        }
    },
    inputs: {
        references: [],      # IDs/references to input rows
        mock_values: {}      # For testing/preview
    },
    calculation: {
        type: str,          # Calculation type identifier
        params: {}          # Calculation-specific parameters
    },
    output: {
        type: str,          # Expected output type
        validation: {}      # Output validation rules
    }
}
```

## Calculation Flow

### 1. Dependency Resolution
- Rows are calculated in order of their index
- Within same index, steps determine execution order
- System creates a Directed Acyclic Graph (DAG) of dependencies
- Automatic index calculation: max(input_indices) + 1

### 2. Time Series Processing
- Calculations proceed period by period
- For each period:
  1. Calculate all index 0 rows
  2. Proceed to index 1 rows
  3. Continue until all indices are processed
- Handle different periodicities (monthly, quarterly, yearly)

### Example Calculation Flow

#### Total Revenue Node Example
```
1. Volume Sold (index: 0, step: 1)
   ├── Inputs: [Total Population, Percentage]
   ├── Local Variables: { Percentage: 0.05 }
   └── Calculation: multiplication

2. Average Price (index: 0, step: 2)
   ├── Inputs: [Historical Data]
   ├── Local Variables: { Historical Data: [{period, value}] }
   └── Calculation: Simple YoY Forecast

3. Revenue (index: 1, step: 1)
   ├── Inputs: [Volume Sold result, Average Price result]
   ├── Local Variables: {}
   └── Calculation: multiplication
```

## Key Design Considerations

### 1. Dependency Management
- Automatic cycle detection
- Clear error messages for circular dependencies
- Validation of input availability
- Optional vs required inputs

### 2. Data Validation
- Type checking for inputs and outputs
- Range validation
- Time period alignment
- Missing data handling

### 3. Calculation Registry
Each calculation type should specify:
- Required inputs
- Optional inputs
- Output format
- Validation rules
- Error handling behavior

### 4. Testing and Validation
- Mock input system for testing
- Scenario testing
- Expected outputs
- Sensitivity analysis capabilities

### 5. Performance Optimization
- Parallel processing of independent calculations
- Caching of intermediate results
- Batch processing for same-index calculations
- Incremental updates (only recalculate affected rows)

### 6. Error Handling
- Clear error propagation
- Input validation errors
- Calculation errors
- Missing data errors
- Time period mismatches

### 7. Audit and Tracking
- Version control for calculations
- Change tracking
- Result audit trail
- Input contribution tracking

## Edge Cases and Special Considerations

### 1. Data Handling
- Null/undefined values
- Missing periods in time series
- Different time period granularities
- Decimal precision
- Unit conversions

### 2. Time Series Special Cases
- Handling gaps in historical data
- Forward-looking projections
- Seasonal adjustments
- Period alignment between different inputs

### 3. Mock Data System
- Preview calculations
- Testing scenarios
- Validation sets
- Quick prototyping

## Future Considerations

### 1. Extensibility
- New calculation types
- Custom validation rules
- Additional metadata fields
- Enhanced testing capabilities

### 2. Integration Points
- Database structure (Supabase)
- UI components (Weweb)
- API endpoints
- Export/import capabilities

### 3. Performance Enhancements
- Materialized views
- Caching strategies
- Batch processing
- Parallel computation

## Next Steps
1. Database schema design
2. API endpoint specification
3. UI component design
4. Implementation priority order
5. Testing strategy development 