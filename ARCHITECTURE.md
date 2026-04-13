```mermaid
graph TD;
    A[User] -->|Uses| B[Application];
    B -->|Calls| C[Python Module];
    B -->|Executes| D[Shell Script];
    C -->|Returns Data| E[Database];
    D -->|Utilizes| E;
```