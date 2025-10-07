# About the Collaborative Editing Feature

## Explanation of Used Technologies and Libraries

### ProseMirror

[https://prosemirror.net](https://prosemirror.net/)

A WYSIWYG editor library that can be used in web browsers. Similar to Draft.js, but does not rely on specific frameworks like React. It is also used in Atlassian's Confluence. It supports Japanese input without issues and is relatively stable.

The source code is split across multiple repositories, which it may seem comfusing at first; however, it is designed with loose coupling in mind regarding the data model, update processing, and connections to the view. It operates with a data flow akin to React + Redux, where commands (transactions) are issued to update the state, and this new state is applied to the view to change the interface. Therefore, integration with React is relatively easy.

### Y.js

[https://docs.yjs.dev](https://docs.yjs.dev/)

A library that provides various data structures for collaborative editing based on [CRDT](https://qiita.com/everpeace/items/bb73ec64d3e682279d26) as its core. In addition to basic data structures such as arrays and Maps, it also has structures capable of handling XML documents.

It provides bindings for various WYSIWYG editors, including integration with ProseMirror. It uses a utility library called lib0 by the same author, which results in some peculiarities in the code.

## Overview of Implementation

![collab-editor-overview](https://user-images.githubusercontent.com/17793678/145666435-3e13532a-ec8d-49cf-8301-99c3a09ff49a.png)

- Frontend
  - To provide necessary editing features for Rimo, ProseMirror is customized using the following methods:
    - A plugin mechanism is employed to declare a custom UI used at the top of the Transcript, identify areas during audio playback, and define custom transactions to control synchronization states with the backend.
    - Modifications to the behavior of line breaks and deletion keys are managed through the options of the keymap plugin, including the assignment of startTime/endTime and IDs during Transcript splitting and merging.
    - A custom schema is defined to control the document's structure.
  - View parts requiring interaction are implemented using React.
    - Specifically, ProseMirror's Decoration mechanism is used to identify parts of the view to be manipulated, and React components are mounted there using React's Portal or position: absolute techniques.
  - Using a plugin provided by Y.js for ProseMirror integration, a system is implemented where the ProseMirror model is synchronized with Y.js's data structure capable of handling XML documents.
    - The synchronization of clients via WebSocket is based on a publicly published reference implementation of Y.js, with custom modifications made for our implementation.
  - Because ProseMirror and Y.js libraries are large, they are implemented as a separate package called collab-editor to avoid slowing down the loading of unrelated pages. The parts that utilize them can be loaded via Dynamic Import.
- Backend
  - A WebSocket server is implemented under the name collab-editor-server.
  - Changes made in the browser are sent to this collab-editor-server and then delivered to other clients.
  - Generally speaking, there is no need to be aware of ProseMirror’s details in the backend. However, because Y.js’s data structures are schema-less (allowing for free tags, marks, and metadata), while ProseMirror requires schema definitions, if new data needs to be handled on the Y.js side, changes to ProseMirror's schema will be required.

## Details of Each Process

### Switching Between Readonly and Editable

Due to current technical limitations, starting up the WebSocket server takes time, so we want to avoid making users wait for this startup. Additionally, many users may only wish to view the content without editing. Therefore, the system is designed to display a Readonly view as quickly as possible when a user accesses it, while preparing the necessary WebSocket server for editing in the background, switching from Readonly to Editable once the setup is complete.

### Synchronization Between Client and Server

The CRDT technology that Y.js is based on is characterized by its ability to read and write as long as the nodes (browsers or servers) are alive, even if the network fails. In the context of collaborative editing in a web browser, there can be numerous instances where new users join mid-session, the page is reloaded, or the server restarts due to deployment or unexpected errors, resulting in node failures.

Thus, Y.js offers a mechanism to synchronize data between nodes when new nodes are added. The basic mechanism involves Y.js maintaining a history of changes (State Vector). When one node sends the head of its State Vector, the receiving node sends the differential changes since that State Vector. This process is performed bidirectionally to complete the data synchronization between nodes. In this case, synchronization occurs between the browser and server. After synchronization completes, the exchange of change messages begins.

While the synchronization generally works well, Y.js's data structures tend to grow large, often requiring several megabytes of data to synchronize when starting from an empty state. In modern Safari browsers, if the size of a WebSocket frame exceeds a certain limit, it results in a "Message too long" error. To avoid this, a presync mechanism has been independently implemented. This mechanism is straightforward: before establishing a WebSocket connection, an HTTP GET request is sent to the same server to receive the current state. Then, a Y.js document is prepared based on that state before starting the WebSocket connection and original synchronization. This greatly reduces the necessary changes in the WebSocket synchronization, resulting in smaller message sizes.

The message size limitation can also pose problems in other scenarios. For example, if a user cuts and pastes the entire body content, several megabytes of changes can be sent at once, potentially hitting the limit. A fundamental solution would require handling message fragmentation, which is currently not implemented.

### Data Persistence and Snapshots

Even with robust synchronization mechanisms, data can be lost if all nodes fail, necessitating the need for data persistence. Also, during collaborative editing, automatic saving of data can lead to accidental changes that may be irreversible. To enable reverting to a previous state, it is essential to save snapshots of the data.

The responsibility for this persistence lies with the WebSocket server.

While it is possible to save every change as a snapshot, this can lead to data bloat and make it challenging for users to determine which version they are on. Therefore, data is saved under the following conditions:

- If more than five minutes have passed since the last snapshot was saved during editing (five minutes is an empirical value).
- When there are no clients accessing the targeted document.
- When a new client connects to the document being edited.
  - Synchronization of data between the server and clients occurs at this time, and since this is when discrepancies are likely to happen, a snapshot is saved just before the synchronization.
- When a termination signal is sent.
  - This is done to prevent loss of in-memory state when the server stops. It is crucial to ensure that the original data can be restored upon restart.

However, if there have been no changes since the last save, saving may not occur in these cases either.
