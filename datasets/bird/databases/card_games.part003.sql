
ALTER TABLE ONLY public.set_translations
    ADD CONSTRAINT set_translations_setcode_fkey FOREIGN KEY (setcode) REFERENCES public.sets(code) ON UPDATE CASCADE ON DELETE CASCADE;

