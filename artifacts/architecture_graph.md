# Interactive Architecture Diagram

```mermaid
graph TD
    tools --> ev_grid_oracle
    training --> ev_grid_oracle
    server --> ev_grid_oracle
    server --> server
    tests --> training
    tests --> server
    tests --> ev_grid_oracle
    ev_grid_oracle --> ev_grid_oracle
    ev_grid_oracle --> server
    viz --> training
    viz --> viz
    viz --> ev_grid_oracle
```
