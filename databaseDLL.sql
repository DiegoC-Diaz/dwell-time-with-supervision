-- Table: public.detection_times

-- DROP TABLE IF EXISTS public.detection_times;

CREATE TABLE IF NOT EXISTS public.detection_times
(
    id bigint NOT NULL DEFAULT nextval('detection_times_id_seq'::regclass),
    zone_id integer NOT NULL,
    time_s integer NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    CONSTRAINT detection_times_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.detection_times
    OWNER to postgres;


    -- Table: public.processes

-- DROP TABLE IF EXISTS public.processes;

CREATE TABLE IF NOT EXISTS public.processes
(
    id bigint NOT NULL DEFAULT nextval('processes_id_seq'::regclass),
    zone_id integer NOT NULL,
    process_name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    model_id character varying(50) COLLATE pg_catalog."default" NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    video_path character varying(255) COLLATE pg_catalog."default",
    is_done boolean DEFAULT false,
    CONSTRAINT processes_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.processes
    OWNER to postgres;



-- Table: public.zones

-- DROP TABLE IF EXISTS public.zones;

CREATE TABLE IF NOT EXISTS public.zones
(
    id integer NOT NULL DEFAULT nextval('zones_id_seq'::regclass),
    zone_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    zone_type character varying(50) COLLATE pg_catalog."default" NOT NULL,
    coordinates jsonb NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT zones_pkey PRIMARY KEY (id),
    CONSTRAINT zones_zone_name_key UNIQUE (zone_name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.zones
    OWNER to postgres;