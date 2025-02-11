
ALTER TABLE ONLY public.badges
    ADD CONSTRAINT badges_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.posthistory
    ADD CONSTRAINT posthistory_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_lasteditoruserid_fkey FOREIGN KEY (lasteditoruserid) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_owneruserid_fkey FOREIGN KEY (owneruserid) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_postid_fkey FOREIGN KEY (postid) REFERENCES public.posts(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;

