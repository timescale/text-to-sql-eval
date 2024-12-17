CREATE TABLE public.author (
    aid bigint NOT NULL,
    homepage text,
    name text,
    oid bigint
);

COMMENT ON COLUMN public.author.aid IS 'Unique identifier for each author';

COMMENT ON COLUMN public.author.homepage IS 'URL of the author''s personal website';

COMMENT ON COLUMN public.author.name IS 'Name of the author';

COMMENT ON COLUMN public.author.oid IS 'Foreign key referencing the organization the author belongs to';

CREATE TABLE public.cite (
    cited bigint,
    citing bigint
);

COMMENT ON COLUMN public.cite.cited IS 'ID of the publication being cited';

COMMENT ON COLUMN public.cite.citing IS 'ID of the publication that is citing another publication';

CREATE TABLE public.conference (
    cid bigint NOT NULL,
    homepage text,
    name text
);

COMMENT ON COLUMN public.conference.cid IS 'Unique identifier for a conference';

COMMENT ON COLUMN public.conference.homepage IS 'The homepage URL for the conference';

COMMENT ON COLUMN public.conference.name IS 'The name of the conference';

CREATE TABLE public.domain (
    did bigint NOT NULL,
    name text
);

COMMENT ON COLUMN public.domain.did IS 'Unique identifier for a domain';

COMMENT ON COLUMN public.domain.name IS 'Name of the domain';

CREATE TABLE public.domain_author (
    aid bigint NOT NULL,
    did bigint NOT NULL
);

COMMENT ON COLUMN public.domain_author.aid IS 'Foreign key referencing the author table''s primary key';

COMMENT ON COLUMN public.domain_author.did IS 'Foreign key referencing the domain table''s primary key';

CREATE TABLE public.domain_conference (
    cid bigint NOT NULL,
    did bigint NOT NULL
);

COMMENT ON COLUMN public.domain_conference.cid IS 'Foreign key referencing the cid column in the conference table';

COMMENT ON COLUMN public.domain_conference.did IS 'Foreign key referencing the did column in the domain table';

CREATE TABLE public.domain_journal (
    did bigint NOT NULL,
    jid bigint NOT NULL
);

COMMENT ON COLUMN public.domain_journal.did IS 'Foreign key referencing the domain table''s primary key';

COMMENT ON COLUMN public.domain_journal.jid IS 'Foreign key referencing the journal table''s primary key';

CREATE TABLE public.domain_keyword (
    did bigint NOT NULL,
    kid bigint NOT NULL
);

COMMENT ON COLUMN public.domain_keyword.did IS 'Foreign key referencing the ''did'' column of the ''domain'' table';

COMMENT ON COLUMN public.domain_keyword.kid IS 'Foreign key referencing the ''kid'' column of the ''keyword'' table';

CREATE TABLE public.domain_publication (
    did bigint NOT NULL,
    pid bigint NOT NULL
);

COMMENT ON COLUMN public.domain_publication.did IS 'Foreign key referencing the domain table''s primary key column (did)';

COMMENT ON COLUMN public.domain_publication.pid IS 'Foreign key referencing the publication table''s primary key column (pid)';

CREATE TABLE public.journal (
    homepage text,
    jid bigint NOT NULL,
    name text
);

COMMENT ON COLUMN public.journal.homepage IS 'The homepage URL for the journal';

COMMENT ON COLUMN public.journal.jid IS 'Unique identifier for a journal';

COMMENT ON COLUMN public.journal.name IS 'The name of the journal';

CREATE TABLE public.keyword (
    keyword text,
    kid bigint NOT NULL
);

COMMENT ON COLUMN public.keyword.keyword IS 'The actual keyword';

COMMENT ON COLUMN public.keyword.kid IS 'Unique identifier for a keyword';

CREATE TABLE public.organization (
    continent text,
    homepage text,
    name text,
    oid bigint NOT NULL
);

COMMENT ON COLUMN public.organization.continent IS 'Continent where the organization is located';

COMMENT ON COLUMN public.organization.homepage IS 'URL of the organization''s homepage';

COMMENT ON COLUMN public.organization.name IS 'Name of the organization';

COMMENT ON COLUMN public.organization.oid IS 'Unique identifier for the organization';

CREATE TABLE public.publication (
    abstract text,
    cid bigint,
    citation_num bigint,
    jid bigint,
    pid bigint NOT NULL,
    reference_num bigint,
    title text,
    year bigint
);

COMMENT ON COLUMN public.publication.abstract IS 'The abstract of the publication';

COMMENT ON COLUMN public.publication.cid IS 'The ID of the conference where the publication was presented';

COMMENT ON COLUMN public.publication.citation_num IS 'The number of citations received by the publication';

COMMENT ON COLUMN public.publication.jid IS 'The ID of the journal where the publication was published';

COMMENT ON COLUMN public.publication.pid IS 'The unique ID of the publication';

COMMENT ON COLUMN public.publication.reference_num IS 'The number of references cited by the publication';

COMMENT ON COLUMN public.publication.title IS 'The title of the publication';

COMMENT ON COLUMN public.publication.year IS 'The year of publication';

CREATE TABLE public.publication_keyword (
    pid bigint NOT NULL,
    kid bigint NOT NULL
);

COMMENT ON COLUMN public.publication_keyword.pid IS 'Foreign key referencing the publication table''s primary key (pid)';

COMMENT ON COLUMN public.publication_keyword.kid IS 'Foreign key referencing the keyword table''s primary key (kid)';

CREATE TABLE public.writes (
    aid bigint NOT NULL,
    pid bigint NOT NULL
);

COMMENT ON COLUMN public.writes.aid IS 'Foreign key referencing the author table''s primary key';

COMMENT ON COLUMN public.writes.pid IS 'Foreign key referencing the publication table''s primary key';

INSERT INTO public.author VALUES (1, 'www.larry.com', 'Larry Summers', 2);
INSERT INTO public.author VALUES (2, 'www.ashish.com', 'Ashish Vaswani', 3);
INSERT INTO public.author VALUES (3, 'www.noam.com', 'Noam Shazeer', 3);
INSERT INTO public.author VALUES (4, 'www.martin.com', 'Martin Odersky', 4);
INSERT INTO public.author VALUES (5, NULL, 'Kempinski', NULL);

INSERT INTO public.cite VALUES (1, 2);
INSERT INTO public.cite VALUES (1, 3);
INSERT INTO public.cite VALUES (1, 4);
INSERT INTO public.cite VALUES (1, 5);
INSERT INTO public.cite VALUES (2, 3);
INSERT INTO public.cite VALUES (2, 5);
INSERT INTO public.cite VALUES (3, 4);
INSERT INTO public.cite VALUES (3, 5);
INSERT INTO public.cite VALUES (4, 5);

INSERT INTO public.conference VALUES (1, 'www.isa.com', 'ISA');
INSERT INTO public.conference VALUES (2, 'www.aaas.com', 'AAAS');
INSERT INTO public.conference VALUES (3, 'www.icml.com', 'ICML');

INSERT INTO public.domain VALUES (1, 'Data Science');
INSERT INTO public.domain VALUES (2, 'Natural Sciences');
INSERT INTO public.domain VALUES (3, 'Computer Science');
INSERT INTO public.domain VALUES (4, 'Sociology');
INSERT INTO public.domain VALUES (5, 'Machine Learning');

INSERT INTO public.domain_author VALUES (1, 2);
INSERT INTO public.domain_author VALUES (1, 4);
INSERT INTO public.domain_author VALUES (2, 3);
INSERT INTO public.domain_author VALUES (2, 1);
INSERT INTO public.domain_author VALUES (2, 5);
INSERT INTO public.domain_author VALUES (3, 5);
INSERT INTO public.domain_author VALUES (3, 3);
INSERT INTO public.domain_author VALUES (4, 3);

INSERT INTO public.domain_conference VALUES (1, 2);
INSERT INTO public.domain_conference VALUES (2, 4);
INSERT INTO public.domain_conference VALUES (3, 5);

INSERT INTO public.domain_journal VALUES (1, 2);
INSERT INTO public.domain_journal VALUES (2, 3);
INSERT INTO public.domain_journal VALUES (5, 4);

INSERT INTO public.domain_keyword VALUES (1, 2);
INSERT INTO public.domain_keyword VALUES (2, 3);

INSERT INTO public.domain_publication VALUES (4, 1);
INSERT INTO public.domain_publication VALUES (2, 2);
INSERT INTO public.domain_publication VALUES (1, 3);
INSERT INTO public.domain_publication VALUES (3, 4);
INSERT INTO public.domain_publication VALUES (3, 5);
INSERT INTO public.domain_publication VALUES (5, 5);

INSERT INTO public.journal VALUES ('www.aijournal.com', 1, 'Journal of Artificial Intelligence Research');
INSERT INTO public.journal VALUES ('www.nature.com', 2, 'Nature');
INSERT INTO public.journal VALUES ('www.science.com', 3, 'Science');
INSERT INTO public.journal VALUES ('www.ml.com', 4, 'Journal of Machine Learning Research');

INSERT INTO public.keyword VALUES ('AI', 1);
INSERT INTO public.keyword VALUES ('Neuroscience', 2);
INSERT INTO public.keyword VALUES ('Machine Learning', 3);
INSERT INTO public.keyword VALUES ('Keyword 4', 4);

INSERT INTO public.organization VALUES ('Asia', 'www.organization1.com', 'Organization 1', 1);
INSERT INTO public.organization VALUES ('North America', 'www.organization2.com', 'Organization 2', 2);
INSERT INTO public.organization VALUES ('North America', 'www.organization3.com', 'Organization 3', 3);
INSERT INTO public.organization VALUES ('Europe', 'www.epfl.com', 'École Polytechnique Fédérale de Lausanne 4', 4);
INSERT INTO public.organization VALUES ('Europe', 'www.organization5.com', 'Organization 5', 5);

INSERT INTO public.publication VALUES ('Abstract 1', 1, 4, 1, 1, 0, 'The Effects of Climate Change on Agriculture', 2020);
INSERT INTO public.publication VALUES ('Abstract 2', 2, 2, 2, 2, 1, 'A Study on the Effects of Social Media on Mental Health', 2020);
INSERT INTO public.publication VALUES ('Abstract 3', 3, 2, 2, 3, 2, 'Data Mining Techniques', 2021);
INSERT INTO public.publication VALUES ('Abstract 4', 3, 1, 2, 4, 2, 'Optimizing GPU Throughput', 2021);
INSERT INTO public.publication VALUES ('Abstract 5', 3, 0, 4, 5, 4, 'Attention is all you need', 2021);

INSERT INTO public.publication_keyword VALUES (1, 2);
INSERT INTO public.publication_keyword VALUES (2, 3);

INSERT INTO public.writes VALUES (1, 1);
INSERT INTO public.writes VALUES (1, 2);
INSERT INTO public.writes VALUES (2, 3);
INSERT INTO public.writes VALUES (2, 4);
INSERT INTO public.writes VALUES (2, 5);
INSERT INTO public.writes VALUES (3, 5);

