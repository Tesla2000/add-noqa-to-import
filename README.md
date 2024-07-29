## Purpose
Suppress length check can be used to automatically annotate too long import statements with # noqa: E501

## Example
### .pre-commit-config
```
repos:
  - repo: https://github.com/Tesla2000/suppress-lenght-check-import
    rev: '0.1.1'
    hooks:
      - id: add-noqa-to-import
        stages: [commit,push]
```
### Before
```
from tests.abstractions.integration.conversations.conversation_base_class import (  # noqa: E501
    ConversationBaseClass,
)
from tests.abstractions.integration.conversations.conversation_base_class import (
    ConversationBaseClass,
)
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass
from tests.abstractions.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass
from tests.abstractions.integration.integration.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration.integration.integration import ConversationBaseClass
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous  # noqa: E501
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous
import folder

var = 1
from tests.abstractions.integration.conversations.conversation_base_class import (  # noqa: E501
    ConversationBaseClass,
)
from tests.abstractions.integration.conversations.conversation_base_class import (
    ConversationBaseClass,
)
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass
from tests.abstractions.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass
from tests.abstractions.integration.integration.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration.integration.integration import ConversationBaseClass
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous  # noqa: E501
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous
import folder
```
### Check
```
Add noqa imports.........................................................Failed
- hook id: add-noqa-to-import
- exit code: 1
- files were modified by this hook

Added noqa: E501 to imports in src/Config.py
```
### After
```
from tests.abstractions.integration.conversations.conversation_base_class import (  # noqa: E501
    ConversationBaseClass,
)
from tests.abstractions.integration.conversations.conversation_base_class import (  # noqa: E501
    ConversationBaseClass,
)
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass
from tests.abstractions.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass
from tests.abstractions.integration.integration.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration.integration.integration import ConversationBaseClass  # noqa: E501
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous  # noqa: E501
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous  # noqa: E501
import folder

var = 1
from tests.abstractions.integration.conversations.conversation_base_class import (  # noqa: E501
    ConversationBaseClass,
)
from tests.abstractions.integration.conversations.conversation_base_class import (  # noqa: E501
    ConversationBaseClass,
)
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass, ConversationBaseClass
from tests.abstractions.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration import ConversationBaseClass
from tests.abstractions.integration.integration.integration import ConversationBaseClass  # noqa: E501
from tests.abstractions.integration.integration.integration import ConversationBaseClass  # noqa: E501
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous  # noqa: E501
import folder.bosabfpasgabgjasfusabfuobsuogsbuafibauofasoubfoasajgpiabjbasfasofbasbfpasbuavous  # noqa: E501
import folder
```

