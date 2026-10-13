# Interactive Architecture Diagram

```mermaid
graph TD
    viz --> training
    viz --> viz
    viz --> ev_grid_oracle
    server --> server
    server --> ev_grid_oracle
    ev_grid_oracle --> server
    ev_grid_oracle --> ev_grid_oracle
    tools --> ev_grid_oracle
    training --> ev_grid_oracle
    tests --> server
    tests --> training
    tests --> ev_grid_oracle
```
