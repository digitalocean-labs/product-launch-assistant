def create_launch_timeline_diagram(launch_plan_text: str) -> str:
    diagram = """```mermaid
graph TD
    A[Pre-Launch Phase] --> B[Market Research]
    B --> C[Product Development]
    C --> D[Beta Testing]
    D --> E[Launch Phase]
    E --> F[Marketing Campaign]
    F --> G[Sales Launch]
    G --> H[Post-Launch Phase]
    H --> I[Customer Feedback]
    I --> J[Performance Analysis]
    J --> K[Optimization]
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style H fill:#e8f5e8
```"""
    return diagram


