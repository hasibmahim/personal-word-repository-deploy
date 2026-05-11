# Deadline 5 Notes

This folder gathers the client and auxiliary-service material used for the Deadline 5 submission.

## Files in this folder

- `client_overview.md`
  Client purpose, rationale, and feature-to-endpoint mapping.
- `client_diagrams.md`
  Use-case, interface layout, and workflow diagrams in Mermaid.
- `auxiliary_service_design.md`
  Auxiliary service purpose, endpoint overview, and communication diagram.
- `demo_checklists.md`
  Step-by-step demo script and evidence capture checklist.

## Current limitations

- The client is a terminal client, not a graphical web client.
- The auxiliary service derives data live from the main API and does not keep a separate cache database yet.
- The client still uses local state for saved users and the active selected word, even though word and category browsing now comes from live collection endpoints.
