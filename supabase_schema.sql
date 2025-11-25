CREATE TABLE audit_results (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  status text NOT NULL,
  result text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);
