# Market Mapper Calculation System Design

## Overview
This document outlines the design of the calculation system used in Market Mapper. The system is built around nodes containing rows, where each row can have multiple calculation steps stored in a dedicated row_calculations table. Each step can have its own inputs, local variables, and calculation logic. This design enables flexible and maintainable calculations while ensuring proper dependency management.

## Core Concepts

### 1. Node Structure
A node represents a logical grouping of related calculations. For example, a "Total Revenue" node might contain:
- Revenue (with multiple calculation steps)

### 2. Database Structure

#### Row Table
```sql
CREATE TABLE node_rows (
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL,
    index INTEGER NOT NULL,
    name VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);

-- Enable RLS
ALTER TABLE node_rows ENABLE ROW LEVEL SECURITY;

-- Simple policy: all access for authenticated users
CREATE POLICY "Allow all access for authenticated users" ON node_rows
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
```

#### Row Calculations Table
```sql
CREATE TABLE row_calculations (
    id UUID PRIMARY KEY,
    row_id UUID NOT NULL,
    step_number INTEGER NOT NULL,
    calculation_type calculation_type NOT NULL DEFAULT 'empty',
    local_variables JSONB DEFAULT '{}',
    inputs JSONB DEFAULT '{"references": [], "mock_values": {}}',
    output_type VARCHAR(50) DEFAULT 'number',
    output_validation JSONB DEFAULT '{}',
    calculation_params JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (row_id) REFERENCES node_rows(id)
);

-- Enable RLS
ALTER TABLE row_calculations ENABLE ROW LEVEL SECURITY;

-- Simple policy: all access for authenticated users
CREATE POLICY "Allow all access for authenticated users" ON row_calculations
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
```

#### Historical Data Tables
```sql
CREATE TABLE historical_data (
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL,
    row_calculation_id UUID NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    source VARCHAR(255) NOT NULL,
    confidence FLOAT,  -- 0-1 scale
    last_updated TIMESTAMP WITH TIME ZONE,
    update_frequency VARCHAR(50),  -- daily, weekly, monthly, etc.
    metadata JSONB DEFAULT '{}',  -- additional source-specific metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (node_id) REFERENCES nodes(id),
    FOREIGN KEY (row_calculation_id) REFERENCES row_calculations(id)
);

-- Enable RLS
ALTER TABLE historical_data ENABLE ROW LEVEL SECURITY;

-- Simple policy: all access for authenticated users
CREATE POLICY "Allow all access for authenticated users" ON historical_data
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE TABLE historical_data_points (
    id UUID PRIMARY KEY,
    historical_data_id UUID NOT NULL,
    period DATE NOT NULL,
    value NUMERIC NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (historical_data_id) REFERENCES historical_data(id),
    UNIQUE (historical_data_id, period)  -- one value per period
);

-- Enable RLS
ALTER TABLE historical_data_points ENABLE ROW LEVEL SECURITY;

-- Simple policy: all access for authenticated users
CREATE POLICY "Allow all access for authenticated users" ON historical_data_points
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
```

#### Forecasted Data Tables
```sql
CREATE TABLE forecasted_data (
    id UUID PRIMARY KEY,
    historical_data_id UUID NOT NULL,
    forecast_method VARCHAR(50) NOT NULL,  -- e.g., 'yoy', 'compound_growth'
    forecast_params JSONB DEFAULT '{}',    -- parameters used for the forecast
    confidence FLOAT,                      -- confidence in the forecast
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (historical_data_id) REFERENCES historical_data(id)
);

-- Enable RLS
ALTER TABLE forecasted_data ENABLE ROW LEVEL SECURITY;

-- Simple policy: all access for authenticated users
CREATE POLICY "Allow all access for authenticated users" ON forecasted_data
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE TABLE forecasted_data_points (
    id UUID PRIMARY KEY,
    forecasted_data_id UUID NOT NULL,
    period DATE NOT NULL,
    value NUMERIC NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (forecasted_data_id) REFERENCES forecasted_data(id),
    UNIQUE (forecasted_data_id, period)  -- one forecasted value per period
);

-- Enable RLS
ALTER TABLE forecasted_data_points ENABLE ROW LEVEL SECURITY;

-- Simple policy: all access for authenticated users
CREATE POLICY "Allow all access for authenticated users" ON forecasted_data_points
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);
```

### 3. Input/Output Structure

#### Input Types
Each row calculation can have two types of inputs:

1. **Historical Inputs**:
   - Used for forecasting future values
   - Must have a mock value for preview in the creator panel
   - Example structure:
   ```json
   {
       "historical_sales": {
           "reference": "historical_data_id",
           "mock_value": 1000,  // Required for preview
           "periodic_data": []  // Will be fetched from historical_data_points
       }
   }
   ```

2. **Row Calculation Inputs**:
   - References to outputs from other calculations
   - No mock value needed (calculated from input mocks)
   - Example structure:
   ```json
   {
       "sales_forecast": {
           "reference": "row_calculation_id",
           "mock_value": null,  // Not needed, will use input's mock output
           "periodic_data": []  // Will use input's periodic output
       }
   }
   ```

#### Output Structure
Each calculation produces:
```json
{
    "mock_output": number,  // Either from mock_value (historical) or calculated from inputs
    "periodic_output": [    // Calculated from periodic_data or input periodic outputs
        {
            "period": "YYYY-MM-DD",
            "value": number
        }
    ]
}
```

### 4. Calculation Types
Available calculation types (as enum):
- multiplication
- division
- addition
- subtraction
- percentage
- forecast_yoy
- compound_growth
- inflation_adjustment
- empty

## Calculation Flow

### 1. Step Chain Processing
- Each row has multiple calculation steps in the row_calculations table
- Steps are executed in order by step_number
- Each step can depend on:
  - Historical data (for forecasting)
  - Results from other row calculations
  - Local variables

### 2. Mock Data Flow
- **For Historical-based Calculations**:
  - Mock value is required in the input
  - Used for preview in the creator panel
  - Helps validate calculation logic
- **For Calculation-based Calculations**:
  - No mock value needed in input
  - Mock output is calculated from input mock outputs
  - Ensures consistency in the calculation chain

### Example Calculation Flow

#### Revenue Forecast Example
```
Revenue Row (index: 1)
├── Step 1: Historical Sales
│   ├── calculation_type: forecast_yoy
│   ├── inputs: {
│   │     "historical_sales": {
│   │         "reference": "historical_data_id",
│   │         "mock_value": 1000,
│   │         "periodic_data": []  // Will be fetched from historical_data_points
│   │     }
│   │ }
│   ├── forecast_params: {
│   │     "method": "yoy",
│   │     "growth_rate": 0.1,
│   │     "periods": 5
│   │ }
│   └── output: {
│         "mock_output": 1100,  // Forecasted from mock_value
│         "periodic_output": []  // Will be calculated from historical_data_points
│       }
│
└── Step 2: Revenue
    ├── calculation_type: multiplication
    ├── inputs: {
    │     "sales_forecast": {
    │         "reference": "step_1_id",
    │         "mock_value": null,  // Not needed
    │         "periodic_data": []  // Will use step_1's periodic_output
    │     },
    │     "price": {
    │         "reference": "price_calculation_id",
    │         "mock_value": null,  // Not needed
    │         "periodic_data": []  // Will use price's periodic_output
    │     }
    │ }
    └── output: {
          "mock_output": 2200,  // Calculated from input mock outputs
          "periodic_output": []  // Will be calculated from input periodic outputs
        }
```

#### Data Flow Example
```
Historical Data:
historical_data
└── id: "hd_123"
    ├── metric_name: "Sales"
    ├── source: "Internal Reports"
    └── historical_data_points
        ├── { period: "2023-01", value: 1000 }
        ├── { period: "2023-02", value: 1100 }
        └── { period: "2023-03", value: 1200 }

Forecasted Data:
forecasted_data
└── id: "fd_456"
    ├── historical_data_id: "hd_123"
    ├── forecast_method: "yoy"
    ├── forecast_params: { "growth_rate": 0.1 }
    └── forecasted_data_points
        ├── { period: "2023-04", value: 1320 }
        ├── { period: "2023-05", value: 1452 }
        └── { period: "2023-06", value: 1597 }

Row Calculation:
row_calculations
└── id: "rc_789"
    ├── row_calculation_id: "rc_789"
    ├── calculation_type: "forecast_yoy"
    ├── inputs: {
    │   "historical_sales": {
    │       "reference": "hd_123",
    │       "mock_value": 1000,
    │       "periodic_data": []  // Fetched from historical_data_points
    │   }
    │ }
    └── output: {
          "mock_output": 1100,
          "periodic_output": []  // Generated from forecasted_data_points
        }
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

### 1. Core Calculation Endpoint
```
POST /api/calculate
- Execute calculation for a specific node/row
- Body: {
    node_id: str,
    row_id: str,
    inputs: {
        market_size: float,
        market_share: float,
        price_point: float,
        growth_rate: float,
        time_horizon: int
    }
}
- Response: {
    revenue: float,
    yearly_revenue: [float],
    market_size: float,
    market_share: float,
    steps: [
        {
            step_number: int,
            result: any,
            execution_time: float
        }
    ]
}
```

### 2. Node Management
```
POST /api/nodes
- Create a new node
- Body: { 
    name: str, 
    description: str, 
    rows: [] 
}

GET /api/nodes
- List all nodes
- Query params: include_rows: bool

GET /api/nodes/{node_id}
- Get node details
- Response includes full row and step structure
```

### 3. Data Management
```
POST /api/data/historical
- Upload historical data for calculations
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
```

### 4. Weweb Integration
The API is designed to work seamlessly with Weweb:

1. **Action Setup**:
```javascript
{
    "market_size": wwElement.marketSize,
    "market_share": wwElement.marketShare,
    "price_point": wwElement.pricePoint,
    "growth_rate": wwElement.growthRate,
    "time_horizon": wwElement.timeHorizon
}
```

2. **Response Handling**:
```javascript
// Total revenue
const totalRevenue = result.revenue;

// Yearly breakdown
const yearlyRevenues = result.yearly_revenue;

// Step results
const stepResults = result.steps;
```

### 5. Error Handling
The API returns appropriate HTTP status codes:
- 200: Successful calculation
- 422: Invalid input data
- 500: Server error

Error responses include:
```json
{
    "detail": "Error message",
    "step": "step_number",
    "input": "input_name"
}
```

### 6. Row Management
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

### 7. Data Management
```
POST /api/data/mock
- Create mock data for testing
- Body: {
    node_id: str,
    row_id: str,
    step_number: int,
    data: any
}
```

### 8. Validation and Testing
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

### 9. Row Calculations Management
```
POST /api/rows/{row_id}/calculations
- Create a new calculation step
- Body: {
    step_number: int,
    calculation_type: str,
    local_variables: {},
    inputs: {
        historical_data: {
            reference: str,
            mock_value: number,
            periodic_data: []
        },
        row_calculation: {
            reference: str,
            mock_value: null,
            periodic_data: []
        }
    },
    output_type: str,
    output_validation: {},
    calculation_params: {}
}

GET /api/rows/{row_id}/calculations
- List all calculation steps for a row
- Query params: include_results: bool

PUT /api/rows/{row_id}/calculations/{calculation_id}
- Update calculation step
- Body: same as POST

DELETE /api/rows/{row_id}/calculations/{calculation_id}
- Delete calculation step
``` 