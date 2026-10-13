# Interactive Architecture Diagram

```mermaid
graph TD
    tools --> ev_grid_oracle
    training --> ev_grid_oracle
    server --> server
    server --> ev_grid_oracle
    tests --> training
    tests --> server
    tests --> ev_grid_oracle
    ev_grid_oracle --> server
    ev_grid_oracle --> ev_grid_oracle
    viz --> training
    viz --> ev_grid_oracle
    viz --> viz
```
