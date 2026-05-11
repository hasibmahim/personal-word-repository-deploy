# Client Diagrams

## Use-case diagram

```mermaid
flowchart LR
    Learner((Learner))

    UC1[Create user]
    UC2[Load saved user]
    UC3[View dashboard]
    UC4[Create and edit words]
    UC5[Create and edit categories]
    UC6[Select word]
    UC7[Create and edit translations]
    UC8[List parts of speech]
    UC9[Open study packs]

    Learner --> UC1
    Learner --> UC2
    Learner --> UC3
    Learner --> UC4
    Learner --> UC5
    Learner --> UC6
    Learner --> UC7
    Learner --> UC8
    Learner --> UC9
```

## Interface layout

```mermaid
flowchart TD
    Main[Main Menu]
    User[User Menu]
    Dashboard[Dashboard Summary]
    Words[Words Menu]
    Categories[Categories Menu]
    Translations[Translations Menu]
    POS[Parts of Speech View]
    Study[Study Packs Menu]

    Main --> User
    Main --> Dashboard
    Main --> Words
    Main --> Categories
    Main --> Translations
    Main --> POS
    Main --> Study
```

## Workflow diagram

```mermaid
flowchart TD
    Start[Start client] --> Health[Check /healthz]
    Health --> UserFlow[Create or load user]
    UserFlow --> CategoryFlow[Optional: create category]
    CategoryFlow --> WordFlow[Create word]
    WordFlow --> SelectWord[Select word]
    SelectWord --> TranslationFlow[Create translation]
    TranslationFlow --> Dashboard[Open dashboard]
    Dashboard --> StudyFlow[Optional: open Study Packs]
    StudyFlow --> MoreWork{Continue?}
    MoreWork -->|Yes| UserFlow
    MoreWork -->|No| End[Quit]
```

## Notes for the report

- These diagrams intentionally model the terminal interface, because that is the implemented client.
- If you export the report to PDF, verify Mermaid rendering first or replace these with screenshots of the same structure.
