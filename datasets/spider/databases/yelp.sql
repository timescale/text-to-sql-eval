CREATE TABLE public.business (
    bid bigint,
    business_id text,
    name text,
    full_address text,
    city text,
    latitude text,
    longitude text,
    review_count bigint,
    is_open bigint,
    state text
);

COMMENT ON COLUMN public.business.bid IS 'The unique identifier for the business';

COMMENT ON COLUMN public.business.business_id IS 'The unique identifier for the business';

COMMENT ON COLUMN public.business.name IS 'The name of the business. All apostrophes use ’ instead of '' to avoid SQL errors.';

COMMENT ON COLUMN public.business.full_address IS 'The full address of the business';

COMMENT ON COLUMN public.business.city IS 'The city where the business is located';

COMMENT ON COLUMN public.business.latitude IS 'The latitude of the business location';

COMMENT ON COLUMN public.business.longitude IS 'The longitude of the business location';

COMMENT ON COLUMN public.business.review_count IS 'The number of reviews for the business';

COMMENT ON COLUMN public.business.is_open IS 'Indicates whether the business is currently open or closed (1 for open, 0 for closed)';

COMMENT ON COLUMN public.business.state IS 'The US state where the business is located, represented by two-letter abbreviations (eg. ''CA'', ''NV'', ''NY'', etc.)';

CREATE TABLE public.category (
    id bigint,
    business_id text,
    category_name text
);

COMMENT ON COLUMN public.category.id IS 'Unique identifier for each category';

COMMENT ON COLUMN public.category.business_id IS 'Identifier for the business associated with the category';

COMMENT ON COLUMN public.category.category_name IS 'Name of the category. Eg ''Bistro'', ''Diner'', ''Pizza''';

CREATE TABLE public.checkin (
    cid bigint,
    business_id text,
    count bigint,
    day text
);

COMMENT ON COLUMN public.checkin.cid IS 'Unique identifier for the daily check-in count';

COMMENT ON COLUMN public.checkin.business_id IS 'Unique identifier for the business where the check-in occurred';

COMMENT ON COLUMN public.checkin.count IS 'Total number of check-ins at a business on a given day';

COMMENT ON COLUMN public.checkin.day IS 'Day of the week when the check-ins occurred. Eg. ''Monday'', ''Tuesday'', etc.';

CREATE TABLE public.neighbourhood (
    id bigint,
    business_id text,
    neighbourhood_name text
);

COMMENT ON COLUMN public.neighbourhood.id IS 'Unique identifier for each neighbourhood';

COMMENT ON COLUMN public.neighbourhood.business_id IS 'Identifier for each business in the neighbourhood';

COMMENT ON COLUMN public.neighbourhood.neighbourhood_name IS 'Name of the neighbourhood where the business is located';

CREATE TABLE public.review (
    rid bigint,
    business_id text,
    user_id text,
    rating real,
    text text,
    year bigint,
    month text
);

COMMENT ON COLUMN public.review.rid IS 'The unique identifier for each review.';

COMMENT ON COLUMN public.review.business_id IS 'The unique identifier for the business being reviewed.';

COMMENT ON COLUMN public.review.user_id IS 'The unique identifier for the user who posted the review.';

COMMENT ON COLUMN public.review.rating IS 'The rating given by the user for the business, on a scale of 1 to 5.';

COMMENT ON COLUMN public.review.text IS 'The text of the review. All apostrophes use ’ instead of '' to avoid SQL errors.';

COMMENT ON COLUMN public.review.year IS 'The year in which the review was posted.';

COMMENT ON COLUMN public.review.month IS 'The month in which the review was posted. Eg. ''January'', ''February'', etc.';

CREATE TABLE public.tip (
    tip_id bigint,
    business_id text,
    text text,
    user_id text,
    likes bigint,
    year bigint,
    month text
);

COMMENT ON COLUMN public.tip.tip_id IS 'Unique identifier for the tip';

COMMENT ON COLUMN public.tip.business_id IS 'Unique identifier for the business where the tip was created.';

COMMENT ON COLUMN public.tip.text IS 'Text content of the tip. All apostrophes use ’ instead of '' to avoid SQL errors.';

COMMENT ON COLUMN public.tip.user_id IS 'Unique identifier for the user who created the tip';

COMMENT ON COLUMN public.tip.year IS 'Year when the tip was created';

COMMENT ON COLUMN public.tip.month IS 'Month when the tip was created. Eg. ''January'', ''February'', etc.';

CREATE TABLE public.users (
    uid bigint,
    user_id text,
    name text
);

COMMENT ON COLUMN public.users.uid IS 'Unique identifier for each user';

COMMENT ON COLUMN public.users.user_id IS 'Unique user ID assigned by the system';

COMMENT ON COLUMN public.users.name IS 'Name of the user';

INSERT INTO public.business VALUES (1, 'abc123', 'Joe’s Pizza', '123 Main St', 'San Francisco', '37.7749295', '-122.4194155', 3, 0, 'CA');
INSERT INTO public.business VALUES (2, 'def456', 'Peter’s Cafe', '456 Elm St', 'New York', '40.712776', '-74.005974', 4, 1, 'NY');
INSERT INTO public.business VALUES (3, 'ghi789', 'Anna’s Diner', '789 Oak St', 'Los Angeles', '34.052235', '-118.243683', 5, 0, 'CA');
INSERT INTO public.business VALUES (4, 'jkl012', 'Mark’s Bistro', '012 Maple St', 'San Francisco', '37.7749295', '-122.4194155', 4, 1, 'CA');
INSERT INTO public.business VALUES (5, 'mno345', 'Lily’s Bakery', '345 Walnut St', 'New York', '40.712776', '-74.005974', 3, 1, 'NY');
INSERT INTO public.business VALUES (6, 'xyz123', 'Izza’s Pizza', '83 Main St', 'San Francisco', '37.8749295', '-122.5194155', 2, 1, 'CA');
INSERT INTO public.business VALUES (7, 'uvw456', 'Sashays Cafe', '246 Elm St', 'New York', '40.812776', '-74.105974', 2, 1, 'NY');

INSERT INTO public.category VALUES (1, 'abc123', 'Pizza');
INSERT INTO public.category VALUES (2, 'def456', 'Cafe');
INSERT INTO public.category VALUES (3, 'ghi789', 'Diner');
INSERT INTO public.category VALUES (4, 'jkl012', 'Bistro');
INSERT INTO public.category VALUES (5, 'mno345', 'Bakery');
INSERT INTO public.category VALUES (1, 'xyz123', 'Pizza');
INSERT INTO public.category VALUES (2, 'uvw456', 'Cafe');

INSERT INTO public.checkin VALUES (1, 'abc123', 10, 'Monday');
INSERT INTO public.checkin VALUES (2, 'def456', 20, 'Tuesday');
INSERT INTO public.checkin VALUES (3, 'ghi789', 15, 'Wednesday');
INSERT INTO public.checkin VALUES (4, 'jkl012', 30, 'Thursday');
INSERT INTO public.checkin VALUES (5, 'mno345', 25, 'Friday');
INSERT INTO public.checkin VALUES (6, 'abc123', 13, 'Tuesday');
INSERT INTO public.checkin VALUES (7, 'def456', 14, 'Wednesday');
INSERT INTO public.checkin VALUES (8, 'ghi789', 8, 'Thursday');
INSERT INTO public.checkin VALUES (9, 'jkl012', 21, 'Saturday');
INSERT INTO public.checkin VALUES (10, 'mno345', 24, 'Friday');
INSERT INTO public.checkin VALUES (11, 'xyz123', 10, 'Saturday');
INSERT INTO public.checkin VALUES (12, 'uvw456', 2, 'Monday');

INSERT INTO public.neighbourhood VALUES (1, 'abc123', 'Downtown');
INSERT INTO public.neighbourhood VALUES (2, 'def456', 'Midtown');
INSERT INTO public.neighbourhood VALUES (3, 'ghi789', 'Hollywood');
INSERT INTO public.neighbourhood VALUES (4, 'jkl012', 'Downtown');
INSERT INTO public.neighbourhood VALUES (5, 'mno345', 'Upper East Side');
INSERT INTO public.neighbourhood VALUES (6, 'xyz123', 'Downtown');
INSERT INTO public.neighbourhood VALUES (7, 'uvw456', 'Midtown');

INSERT INTO public.review VALUES (1, 'abc123', '1', 4.5, 'Great pizza!', 2021, 'January');
INSERT INTO public.review VALUES (2, 'def456', '2', 4.2, 'Delicious food.', 2021, 'February');
INSERT INTO public.review VALUES (3, 'ghi789', '3', 3.9, 'Average diner.', 2021, 'March');
INSERT INTO public.review VALUES (4, 'jkl012', '4', 4.8, 'Amazing bistro.', 2021, 'April');
INSERT INTO public.review VALUES (5, 'mno345', '5', 4.6, 'Yummy bakery.', 2021, 'January');
INSERT INTO public.review VALUES (6, 'ghi789', '1', 1.2, 'Horrible staff!', 2021, 'April');
INSERT INTO public.review VALUES (7, 'def456', '2', 4.9, 'Second visit. I’m loving it.', 2021, 'May');
INSERT INTO public.review VALUES (8, 'xyz123', '3', 0.5, 'Hate it', 2021, 'June');
INSERT INTO public.review VALUES (9, 'uvw456', '4', 4, 'Not bad.', 2021, 'July');
INSERT INTO public.review VALUES (10, 'abc123', '5', 4.6, 'Very goody.', 2022, 'January');
INSERT INTO public.review VALUES (11, 'def456', '1', 3, 'Average', 2022, 'February');
INSERT INTO public.review VALUES (12, 'ghi789', '2', 4, 'Not bad.', 2022, 'March');
INSERT INTO public.review VALUES (13, 'jkl012', '3', 4.5, 'Second time here.', 2022, 'April');
INSERT INTO public.review VALUES (14, 'mno345', '4', 4.6, 'Third time here.', 2022, 'May');
INSERT INTO public.review VALUES (15, 'xyz123', '5', 3.5, 'Wont come again.', 2022, 'June');
INSERT INTO public.review VALUES (16, 'uvw456', '1', 4, 'Quite good.', 2022, 'July');
INSERT INTO public.review VALUES (17, 'mno345', '2', 4.6, 'Superb.', 2022, 'July');
INSERT INTO public.review VALUES (18, 'jkl012', '3', 5, 'WOwowow.', 2022, 'August');
INSERT INTO public.review VALUES (19, 'jkl012', '4', 4.8, 'Lovin it.', 2022, 'September');
INSERT INTO public.review VALUES (20, 'ghi789', '5', 1.5, 'Worst experience ever.', 2023, 'September');
INSERT INTO public.review VALUES (21, 'abc123', '1', 4.6, 'Very goody.', 2024, 'March    ');
INSERT INTO public.review VALUES (22, 'def456', '2', 3, 'Average', 2024, 'April    ');
INSERT INTO public.review VALUES (23, 'ghi789', '3', 4, 'Not bad.', 2024, 'May      ');

INSERT INTO public.tip VALUES (1, 'abc123', 'Try their pepperoni pizza!', '1', NULL, 2021, 'January');
INSERT INTO public.tip VALUES (2, 'def456', 'Their coffee is amazing.', '2', NULL, 2021, 'February');
INSERT INTO public.tip VALUES (3, 'ghi789', 'The pancakes are delicious.', '3', NULL, 2021, 'March');
INSERT INTO public.tip VALUES (4, 'jkl012', 'Highly recommend the steak.', '4', NULL, 2021, 'April');
INSERT INTO public.tip VALUES (5, 'mno345', 'Their pastries are to die for.', '5', NULL, 2021, 'May');
INSERT INTO public.tip VALUES (6, 'xyz123', 'Don’t waste your money.', '1', NULL, 2021, 'June');
INSERT INTO public.tip VALUES (7, 'uvw456', 'Not bad.', '2', NULL, 2021, 'July');
INSERT INTO public.tip VALUES (8, 'mno345', 'Get the blueberry pancakes!', '1', NULL, 2022, 'January');
INSERT INTO public.tip VALUES (9, 'abc123', 'Try their pepperoni pizza!', '1', NULL, 2022, 'January');
INSERT INTO public.tip VALUES (10, 'def456', 'Their coffee is amazing.', '2', NULL, 2022, 'February');
INSERT INTO public.tip VALUES (11, 'ghi789', 'The pancakes are delicious.', '3', NULL, 2022, 'March');
INSERT INTO public.tip VALUES (12, 'jkl012', 'Highly recommend the steak.', '4', NULL, 2022, 'April');
INSERT INTO public.tip VALUES (13, 'mno345', 'Their pastries are to die for.', '5', NULL, 2022, 'May');
INSERT INTO public.tip VALUES (14, 'xyz123', 'Don’t waste your money.', '1', NULL, 2022, 'June');
INSERT INTO public.tip VALUES (15, 'uvw456', 'So-so.', '2', NULL, 2022, 'July');
INSERT INTO public.tip VALUES (16, 'mno345', 'Second time having blueberry pancakes!', '1', NULL, 2022, 'July');
INSERT INTO public.tip VALUES (17, 'jkl012', 'Great happy hour deals.', '5', NULL, 2022, 'August');
INSERT INTO public.tip VALUES (18, 'jkl012', 'Ask for extra sauce.', '3', NULL, 2022, 'September');
INSERT INTO public.tip VALUES (19, 'ghi789', 'Friendly staff.', '4', NULL, 2022, 'October');
INSERT INTO public.tip VALUES (20, 'def456', 'Tasty lattes.', '4', NULL, 2022, 'November');
INSERT INTO public.tip VALUES (21, 'abc123', 'Fresh ingredients.', '2', NULL, 2022, 'December');

INSERT INTO public.users VALUES (1, '1', 'John Doe');
INSERT INTO public.users VALUES (2, '2', 'Jane Smith');
INSERT INTO public.users VALUES (3, '3', 'David Johnson');
INSERT INTO public.users VALUES (4, '4', 'Sarah Williams');
INSERT INTO public.users VALUES (5, '5', 'Michael Brown');

