CREATE TABLE public.author (
    authorid bigint NOT NULL,
    authorname text
);

COMMENT ON COLUMN public.author.authorid IS 'Unique identifier for each author';

COMMENT ON COLUMN public.author.authorname IS 'Name of the author';

CREATE TABLE public.cite (
    citingpaperid bigint NOT NULL,
    citedpaperid bigint NOT NULL
);

COMMENT ON COLUMN public.cite.citingpaperid IS 'The ID of the paper that is doing the citing.';

COMMENT ON COLUMN public.cite.citedpaperid IS 'The ID of the paper that is being cited.';

CREATE TABLE public.dataset (
    datasetid bigint NOT NULL,
    datasetname text
);

COMMENT ON COLUMN public.dataset.datasetid IS 'Unique identifier for each dataset in the table';

COMMENT ON COLUMN public.dataset.datasetname IS 'Name of the dataset';

CREATE TABLE public.field (
    fieldid bigint
);

COMMENT ON COLUMN public.field.fieldid IS 'Unique identifier for each field in the table';

CREATE TABLE public.journal (
    journalid bigint NOT NULL,
    journalname text
);

COMMENT ON COLUMN public.journal.journalid IS 'Unique identifier for each journal entry';

COMMENT ON COLUMN public.journal.journalname IS 'Name or title of the journal';

CREATE TABLE public.keyphrase (
    keyphraseid bigint NOT NULL,
    keyphrasename text
);

COMMENT ON COLUMN public.keyphrase.keyphraseid IS 'Unique identifier for each keyphrase';

COMMENT ON COLUMN public.keyphrase.keyphrasename IS 'The actual keyphrase text';

CREATE TABLE public.paper (
    paperid bigint NOT NULL,
    title text,
    venueid bigint,
    year bigint,
    numciting bigint,
    numcitedby bigint,
    journalid bigint
);

COMMENT ON COLUMN public.paper.paperid IS 'The unique ID of the paper.';

COMMENT ON COLUMN public.paper.title IS 'The title of the paper, enclosed in double quotes if it contains commas.';

COMMENT ON COLUMN public.paper.venueid IS 'The ID of the venue where the paper was published.';

COMMENT ON COLUMN public.paper.year IS 'The year the paper was published.';

COMMENT ON COLUMN public.paper.numciting IS 'The number of papers that this paper cites.';

COMMENT ON COLUMN public.paper.numcitedby IS 'The number of papers that cite this paper.';

COMMENT ON COLUMN public.paper.journalid IS 'The ID of the journal where the paper was published.';

CREATE TABLE public.paperdataset (
    paperid bigint,
    datasetid bigint
);

COMMENT ON COLUMN public.paperdataset.paperid IS 'Unique identifier for each paper in the dataset';

COMMENT ON COLUMN public.paperdataset.datasetid IS 'Unique identifier for each dataset that the paper belongs to';

CREATE TABLE public.paperfield (
    fieldid bigint,
    paperid bigint
);

COMMENT ON COLUMN public.paperfield.fieldid IS 'Unique identifier for each field in the table';

COMMENT ON COLUMN public.paperfield.paperid IS 'Unique identifier for each paper in the table';

CREATE TABLE public.paperkeyphrase (
    paperid bigint,
    keyphraseid bigint
);

COMMENT ON COLUMN public.paperkeyphrase.paperid IS 'The ID of the paper associated with the keyphrase.';

COMMENT ON COLUMN public.paperkeyphrase.keyphraseid IS 'The ID of the keyphrase associated with the paper.';

CREATE TABLE public.venue (
    venueid bigint NOT NULL,
    venuename text
);

COMMENT ON COLUMN public.venue.venueid IS 'Unique identifier for each venue';

COMMENT ON COLUMN public.venue.venuename IS 'Name of the venue';

CREATE TABLE public.writes (
    paperid bigint,
    authorid bigint
);

COMMENT ON COLUMN public.writes.paperid IS 'The unique identifier for a paper in the writes table.';

COMMENT ON COLUMN public.writes.authorid IS 'The unique identifier for an author in the writes table.';

INSERT INTO public.author VALUES (1, 'John Smith');
INSERT INTO public.author VALUES (2, 'Emily Johnson');
INSERT INTO public.author VALUES (3, 'Michael Brown');
INSERT INTO public.author VALUES (4, 'Sarah Davis');
INSERT INTO public.author VALUES (5, 'David Wilson');
INSERT INTO public.author VALUES (6, 'Jennifer Lee');
INSERT INTO public.author VALUES (7, 'Robert Moore');
INSERT INTO public.author VALUES (8, 'Linda Taylor');
INSERT INTO public.author VALUES (9, 'William Anderson');
INSERT INTO public.author VALUES (10, 'Karen Martinez');

INSERT INTO public.cite VALUES (1, 2);
INSERT INTO public.cite VALUES (2, 3);
INSERT INTO public.cite VALUES (3, 4);
INSERT INTO public.cite VALUES (4, 5);
INSERT INTO public.cite VALUES (5, 1);
INSERT INTO public.cite VALUES (3, 5);
INSERT INTO public.cite VALUES (4, 2);
INSERT INTO public.cite VALUES (1, 4);
INSERT INTO public.cite VALUES (3, 1);

INSERT INTO public.dataset VALUES (1, 'COVID-19 Research');
INSERT INTO public.dataset VALUES (2, 'Machine Learning Datasets');
INSERT INTO public.dataset VALUES (3, 'Climate Change Data');
INSERT INTO public.dataset VALUES (4, 'Social Media Analysis');

INSERT INTO public.field VALUES (1);
INSERT INTO public.field VALUES (2);
INSERT INTO public.field VALUES (3);
INSERT INTO public.field VALUES (4);

INSERT INTO public.journal VALUES (1, 'Nature');
INSERT INTO public.journal VALUES (2, 'Science');
INSERT INTO public.journal VALUES (3, 'IEEE Transactions on Pattern Analysis and Machine Intelligence');
INSERT INTO public.journal VALUES (4, 'International Journal of Mental Health');

INSERT INTO public.keyphrase VALUES (1, 'Machine Learning');
INSERT INTO public.keyphrase VALUES (2, 'Climate Change');
INSERT INTO public.keyphrase VALUES (3, 'Social Media');
INSERT INTO public.keyphrase VALUES (4, 'COVID-19');
INSERT INTO public.keyphrase VALUES (5, 'Mental Health');

INSERT INTO public.paper VALUES (1, 'A Study on Machine Learning Algorithms', 1, 2020, 2, 2, 3);
INSERT INTO public.paper VALUES (2, 'The Effects of Climate Change on Agriculture', 1, 2020, 1, 2, 1);
INSERT INTO public.paper VALUES (3, 'Social Media and Mental Health', 2, 2019, 3, 1, 4);
INSERT INTO public.paper VALUES (4, 'COVID-19 Impact on Society', 1, 2020, 2, 2, 2);
INSERT INTO public.paper VALUES (5, 'Machine Learning in Tackling Climate Change', 2, 2019, 1, 2, 3);

INSERT INTO public.paperdataset VALUES (1, 2);
INSERT INTO public.paperdataset VALUES (2, 3);
INSERT INTO public.paperdataset VALUES (3, 4);
INSERT INTO public.paperdataset VALUES (4, 1);
INSERT INTO public.paperdataset VALUES (5, 2);
INSERT INTO public.paperdataset VALUES (5, 3);

INSERT INTO public.paperfield VALUES (1, 1);
INSERT INTO public.paperfield VALUES (2, 2);
INSERT INTO public.paperfield VALUES (3, 3);
INSERT INTO public.paperfield VALUES (4, 4);
INSERT INTO public.paperfield VALUES (1, 5);

INSERT INTO public.paperkeyphrase VALUES (1, 1);
INSERT INTO public.paperkeyphrase VALUES (2, 2);
INSERT INTO public.paperkeyphrase VALUES (3, 3);
INSERT INTO public.paperkeyphrase VALUES (3, 5);
INSERT INTO public.paperkeyphrase VALUES (4, 4);
INSERT INTO public.paperkeyphrase VALUES (5, 1);
INSERT INTO public.paperkeyphrase VALUES (5, 2);

INSERT INTO public.venue VALUES (1, 'Conference on Machine Learning');
INSERT INTO public.venue VALUES (2, 'International Journal of Climate Change');
INSERT INTO public.venue VALUES (3, 'Social Media Analysis Workshop');

INSERT INTO public.writes VALUES (1, 1);
INSERT INTO public.writes VALUES (2, 2);
INSERT INTO public.writes VALUES (3, 3);
INSERT INTO public.writes VALUES (4, 4);
INSERT INTO public.writes VALUES (5, 5);
INSERT INTO public.writes VALUES (1, 3);
INSERT INTO public.writes VALUES (1, 4);
INSERT INTO public.writes VALUES (2, 3);
INSERT INTO public.writes VALUES (4, 5);
INSERT INTO public.writes VALUES (5, 1);
INSERT INTO public.writes VALUES (2, 1);
INSERT INTO public.writes VALUES (4, 3);
INSERT INTO public.writes VALUES (4, 6);
INSERT INTO public.writes VALUES (2, 7);
INSERT INTO public.writes VALUES (2, 8);
INSERT INTO public.writes VALUES (2, 9);

