# DATABASE DOCUMENTATION

### Main Diagram

![img](./MainDiagram.svg)

## Tables

1. [Default.affirmative_drafts](#table%20default.affirmative\_drafts) 
2. [Default.extracted_emails](#table%20default.extracted\_emails) 
3. [Default.negative_drafts](#table%20default.negative\_drafts) 
4. [Default.reports](#table%20default.reports) 
5. [Default.summaries](#table%20default.summaries) 

### Table Default.affirmative_drafts 

|Idx |Name |Data Type |
|---|---|---|
| * &#128273;  | affirmative\_id| INTEGER AUTOINCREMENT |
| &#11016; | email\_id| TEXT  |
|  | model| TEXT  |
|  | temperature| NUMERIC  |
|  | system\_prompt| TEXT  |
|  | user\_prompt| TEXT  |
|  | affirmative\_draft| TEXT  |
|  | processing\_timestamp| DATETIME  |
|  | prompt\_tokens| INTEGER  |
|  | completion\_tokens| INTEGER  |
|  | total\_tokens| INTEGER  |

##### Foreign Keys

|Type |Name |On |
|---|---|---|
|  | FK_affirmative_drafts extracted_emails | ( email\_id ) ref [Default.extracted\_emails](#extracted\_emails) (email\_id) |

### Table Default.extracted_emails 

|Idx |Name |Data Type |
|---|---|---|
| * &#128273;  &#11019; | email\_id| TEXT  |
|  | thread\_id| TEXT  |
|  | labels| TEXT  |
|  | sent\_datetime| DATETIME  |
|  | subject| TEXT  |
|  | sender| TEXT  |
|  | email\_from| TEXT  |
|  | body| TEXT  |
|  | processed| NUMERIC  |
|  | extraction\_timestamp| DATETIME  |

### Table Default.negative_drafts 

|Idx |Name |Data Type |
|---|---|---|
| * &#128273;  | negative\_id| INTEGER AUTOINCREMENT |
| &#11016; | email\_id| TEXT  |
|  | model| TEXT  |
|  | temperature| NUMERIC  |
|  | system\_prompt| TEXT  |
|  | user\_prompt| TEXT  |
|  | negative\_draft| TEXT  |
|  | processing\_timestamp| DATETIME  |
|  | prompt\_tokens| INTEGER  |
|  | completion\_tokens| INTEGER  |
|  | total\_tokens| INTEGER  |

##### Foreign Keys

|Type |Name |On |
|---|---|---|
|  | FK_negative_drafts extracted_emails | ( email\_id ) ref [Default.extracted\_emails](#extracted\_emails) (email\_id) |

### Table Default.reports 

|Idx |Name |Data Type |
|---|---|---|
| * &#128273;  | report\_id| INTEGER AUTOINCREMENT |
|  | date\_from| DATETIME  |
|  | date\_to| DATETIME  |
|  | emails\_reported| TEXT  |
|  | model| TEXT  |
|  | temperature| NUMERIC  |
|  | system\_prompt| TEXT  |
|  | user\_prompt| TEXT  |
|  | report| TEXT  |
|  | report\_timestamp| DATETIME  |
|  | prompt\_tokens| INTEGER  |
|  | completion\_tokens| INTEGER  |
|  | total\_tokens| INTEGER  |

### Table Default.summaries 

|Idx |Name |Data Type |
|---|---|---|
| * &#128273;  | summary\_id| INTEGER AUTOINCREMENT |
| &#11016; | email\_id| TEXT  |
|  | model| TEXT  |
|  | temperature| NUMERIC  |
|  | system\_prompt| TEXT  |
|  | user\_prompt| TEXT  |
|  | summary| TEXT  |
|  | processing\_timestamp| DATETIME  |
|  | prompt\_tokens| INTEGER  |
|  | completion\_tokens| INTEGER  |
|  | total\_tokens| INTEGER  |
|  | reported| NUMERIC  |

##### Foreign Keys

|Type |Name |On |
|---|---|---|
|  | FK_summaries extracted_emails | ( email\_id ) ref [Default.extracted\_emails](#extracted\_emails) (email\_id) |
