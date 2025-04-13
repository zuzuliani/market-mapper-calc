# Market Mapper Calculation System Design

## Overview
This document outlines the design of the calculation system used in Market Mapper. The system is built around nodes containing rows, where each row can have multiple calculation steps that form a hierarchical structure. Each step can have its own inputs, local variables, and calculation logic.

## Core Concepts

### 1. Node Structure
A node represents a logical grouping of related calculations. For example, a "Total Revenue" node might contain:
- Revenue (with multiple calculation steps)

### 2. Row Structure
Each row within a node contains a sequence of calculation steps:
```
{
    metadata: {
        index: int,          # Determines calculation order (max(input_indices) + 1)
        name: str,           # Row name
        description: str     # Optional description
    },
    steps: [
        {
            step_number: int,  # Sequential order within row (1.1, 1.2, 1.3)
            local_variables: { # Variables specific to this step
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
                references: [],      # IDs/references to input rows or previous steps
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
    ]
}
```

## Calculation Flow

### 1. Step Chain Processing
- Each row contains a sequence of calculation steps
- Steps are executed in order (1.1 → 1.2 → 1.3)
- Each step can depend on:
  - Results from previous steps in the same row
  - Results from other rows
  - Local variables
  - External inputs

### 2. Index Management
- Index determines model-wide calculation order
- Formula: `index = max(input_indices) + 1`
- Ensures dependencies are calculated before they're needed
- Used for model/simulation steps

### Example Calculation Flow

#### Total Revenue Node Example
```
Revenue Row (index: 1)
├── Step 1.1: Volume Sold (index: 0)
│   ├── Inputs: [Total Population, Percentage]
│   ├── Local Variables: { Percentage: 0.05 }
│   └── Calculation: multiplication
│
├── Step 1.2: Average Price (index: 0)
│   ├── Inputs: [Historical Data]
│   ├── Local Variables: { Historical Data: [{period, value}] }
│   └── Calculation: Simple YoY Forecast
│
└── Step 1.3: Revenue (index: 1)
    ├── Inputs: [Volume Sold result, Average Price result]
    ├── Local Variables: {}
    └── Calculation: multiplication
```

#### Market Share Node Example
```
Market Share Row (index: 2)
├── Step 1.1: Total Market Size (index: 1)
│   ├── Inputs: [Industry Reports]
│   ├── Local Variables: { Growth Rate: 0.03 }
│   └── Calculation: Compound Growth
│
├── Step 1.2: Our Sales (index: 1)
│   ├── Inputs: [Revenue result]
│   ├── Local Variables: { Conversion Rate: 0.8 }
│   └── Calculation: division
│
└── Step 1.3: Market Share (index: 2)
    ├── Inputs: [Our Sales result, Total Market Size result]
    ├── Local Variables: {}
    └── Calculation: percentage
```

#### Cost Analysis Node Example
```
Cost Analysis Row (index: 3)
├── Step 1.1: Fixed Costs (index: 0)
│   ├── Inputs: [Historical Costs]
│   ├── Local Variables: { Inflation Rate: 0.02 }
│   └── Calculation: Inflation Adjustment
│
├── Step 1.2: Variable Costs (index: 1)
│   ├── Inputs: [Volume Sold result]
│   ├── Local Variables: { Cost per Unit: 5.0 }
│   └── Calculation: multiplication
│
└── Step 1.3: Total Costs (index: 2)
    ├── Inputs: [Fixed Costs result, Variable Costs result]
    ├── Local Variables: {}
    └── Calculation: addition
```

## Key Design Considerations

### 1. Step Chain Management
- Sequential execution of steps
- Result passing between steps
- Error handling per step
- Step-specific validation
- Intermediate result storage

### 2. Data Flow
- How to store intermediate results
- Caching strategy for step results
- Memory management for large calculations
- Result visibility in UI
- Data persistence between steps

### 3. Error Handling
- Step-level error handling
- Error propagation through chain
- Partial calculation results
- Recovery mechanisms
- Validation at each step

### 4. Performance Optimization
- Parallel processing of independent steps
- Caching of intermediate results
- Batch processing for same-index calculations
- Incremental updates
- Memory optimization

### 5. Testing and Validation
- Step-level testing
- Chain validation
- Mock data system
- Scenario testing
- Expected outputs

### 6. UI/UX Considerations
- Step chain visualization
- Intermediate result display
- Step modification interface
- Progress tracking
- Error visualization

## Edge Cases and Special Considerations

### 1. Step Chain Edge Cases
- Missing step results
- Circular dependencies between steps
- Variable scope conflicts
- Step reordering
- Partial calculations

### 2. Time Series Handling
- Step-specific time series processing
- Historical data alignment
- Forecast calculations
- Period handling
- Data gaps

### 3. Mock Data System
- Step-level mocking
- Chain testing
- Scenario validation
- Quick prototyping
- Data generation

## Future Considerations

### 1. Extensibility
- New step types
- Custom calculations
- Enhanced validation
- Additional metadata
- Testing capabilities

### 2. Integration Points
- Database structure (Supabase)
- UI components (Weweb)
- API endpoints
- Export/import
- Version control

### 3. Performance Enhancements
- Step parallelization
- Caching strategies
- Batch processing
- Memory optimization
- Calculation optimization

## Next Steps
1. Database schema design
2. API endpoint specification
3. UI component design
4. Implementation priority order
5. Testing strategy development

## API Endpoint Design

### 1. Node Management
```
POST /api/nodes
- Create a new node
- Body: { name: str, description: str, rows: [] }

GET /api/nodes
- List all nodes
- Query params: include_rows: bool

GET /api/nodes/{node_id}
- Get node details
- Response includes full row and step structure

PUT /api/nodes/{node_id}
- Update node metadata
- Body: { name: str, description: str }

DELETE /api/nodes/{node_id}
- Delete node and all its rows
```

### 2. Row Management
```
POST /api/nodes/{node_id}/rows
- Create a new row
- Body: { 
    name: str,
    description: str,
    steps: [
        {
            step_number: int,
            local_variables: {},
            inputs: {},
            calculation: {}
        }
    ]
}

GET /api/nodes/{node_id}/rows
- List all rows in node

GET /api/nodes/{node_id}/rows/{row_id}
- Get row details with all steps

PUT /api/nodes/{node_id}/rows/{row_id}
- Update row structure
- Body: same as POST

DELETE /api/nodes/{node_id}/rows/{row_id}
- Delete row and all its steps
```

### 3. Calculation Execution
```
POST /api/calculate
- Execute calculation for specific node/row
- Body: {
    node_id: str,
    row_id: str,
    period: {
        start: date,
        end: date
    },
    inputs: {
        // Override any inputs for this calculation
    }
}

GET /api/calculate/{calculation_id}
- Get calculation status and results
- Response: {
    status: str,
    progress: float,
    results: {
        steps: [
            {
                step_number: int,
                result: any,
                execution_time: float
            }
        ]
    }
}
```

### 4. Data Management
```
POST /api/data/historical
- Upload historical data
- Body: {
    node_id: str,
    row_id: str,
    data: [
        {
            period: date,
            value: any
        }
    ]
}

GET /api/data/historical
- Get historical data
- Query params: node_id, row_id, start_date, end_date

POST /api/data/mock
- Create mock data for testing
- Body: {
    node_id: str,
    row_id: str,
    step_number: int,
    data: any
}
```

### 5. Validation and Testing
```
POST /api/validate
- Validate node/row structure
- Body: {
    node_id: str,
    row_id: str
}

POST /api/test
- Run test scenarios
- Body: {
    node_id: str,
    scenarios: [
        {
            name: str,
            inputs: {},
            expected_outputs: {}
        }
    ]
}
``` 