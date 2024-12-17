CREATE TABLE public.geographic (
    city_name text,
    county text,
    region text
);

COMMENT ON COLUMN public.geographic.city_name IS 'The name of the city';

COMMENT ON COLUMN public.geographic.county IS 'The name of the county';

COMMENT ON COLUMN public.geographic.region IS 'The name of the region';

CREATE TABLE public.location (
    restaurant_id bigint,
    house_number bigint,
    street_name text,
    city_name text
);

COMMENT ON COLUMN public.location.restaurant_id IS 'Unique identifier for each restaurant';

COMMENT ON COLUMN public.location.house_number IS 'The number assigned to the building where the restaurant is located';

COMMENT ON COLUMN public.location.street_name IS 'The name of the street where the restaurant is located';

COMMENT ON COLUMN public.location.city_name IS 'The name of the city where the restaurant is located';

CREATE TABLE public.restaurant (
    id bigint,
    name text,
    food_type text,
    city_name text,
    rating real
);

COMMENT ON COLUMN public.restaurant.id IS 'Unique identifier for each restaurant';

COMMENT ON COLUMN public.restaurant.name IS 'The name of the restaurant';

COMMENT ON COLUMN public.restaurant.food_type IS 'The type of food served at the restaurant';

COMMENT ON COLUMN public.restaurant.city_name IS 'The city where the restaurant is located';

COMMENT ON COLUMN public.restaurant.rating IS 'The rating of the restaurant on a scale of 0 to 5';

INSERT INTO public.geographic VALUES ('Los Angeles', 'Los Angeles', 'California');
INSERT INTO public.geographic VALUES ('New York', 'New York', 'New York');
INSERT INTO public.geographic VALUES ('San Francisco', 'San Francisco', 'California');
INSERT INTO public.geographic VALUES ('Miami', 'Miami-Dade', 'Florida');
INSERT INTO public.geographic VALUES ('Chicago', 'Cook', 'Illinois');

INSERT INTO public.location VALUES (1, 123, 'Main St', 'Los Angeles');
INSERT INTO public.location VALUES (2, 456, 'Maple Ave', 'Los Angeles');
INSERT INTO public.location VALUES (3, 789, 'Oak St', 'Los Angeles');
INSERT INTO public.location VALUES (4, 321, 'Elm St', 'New York');
INSERT INTO public.location VALUES (5, 654, 'Pine Ave', 'New York');
INSERT INTO public.location VALUES (6, 123, 'Pine Ave', 'New York');
INSERT INTO public.location VALUES (7, 12, 'Market St', 'San Francisco');
INSERT INTO public.location VALUES (8, 34, 'Mission St', 'San Francisco');
INSERT INTO public.location VALUES (9, 56, 'Valencia St', 'San Francisco');
INSERT INTO public.location VALUES (10, 78, 'Ocean Dr', 'Miami');
INSERT INTO public.location VALUES (11, 90, 'Biscayne Rd', 'Miami');

INSERT INTO public.restaurant VALUES (1, 'The Pasta House', 'Italian', 'Los Angeles', 4.5);
INSERT INTO public.restaurant VALUES (2, 'The Burger Joint', 'American', 'Los Angeles', 3.8);
INSERT INTO public.restaurant VALUES (3, 'The Sushi Bar', 'Japanese', 'Los Angeles', 4.2);
INSERT INTO public.restaurant VALUES (4, 'The Pizza Place', 'Italian', 'New York', 4.7);
INSERT INTO public.restaurant VALUES (5, 'The Steakhouse', 'American', 'New York', 3.9);
INSERT INTO public.restaurant VALUES (6, 'The Ramen Shop', 'Japanese', 'New York', 4.3);
INSERT INTO public.restaurant VALUES (7, 'The Tacos & Burritos', 'Mexican', 'San Francisco', 4.1);
INSERT INTO public.restaurant VALUES (8, 'The Vegan Cafe', 'Vegan', 'San Francisco', 4.6);
INSERT INTO public.restaurant VALUES (9, 'The BBQ Joint', 'American', 'San Francisco', 3.7);
INSERT INTO public.restaurant VALUES (10, 'The Seafood Shack', 'Seafood', 'Miami', 4.4);
INSERT INTO public.restaurant VALUES (11, 'The Seafood Shack', 'Seafood', 'Miami', 4.6);

