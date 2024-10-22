-- #================================================================# --
-- #STORED PROCEDURES
-- #================================================================# --
-- # '/show_my_referrals'
-- 6) you can view your referal history (referal link, points earned, users joined, users/points lost)
DELIMITER $$
DROP PROCEDURE IF EXISTS GET_PROMOTOR_INFO;
CREATE PROCEDURE `GET_PROMOTOR_INFO`(
    IN p_tg_user_id VARCHAR(40), -- '581475171'
    IN p_start_idx INT(10),
    IN p_count INT(10),
    IN p_desc BOOLEAN
	)
BEGIN
    SELECT id FROM users WHERE tg_user_id = p_tg_user_id INTO @v_user_id;
    SELECT referral_points FROM promotors WHERE fk_user_id = @v_user_id INTO @v_pts_earned;
    SELECT tg_user_group_url FROM promotors WHERE fk_user_id = @v_user_id INTO @v_ref_link;
    SELECT COUNT(*) FROM referrals WHERE tg_user_group_url = @v_ref_link AND is_active = FALSE INTO @v_usr_lost_cnt;
    SELECT COUNT(*) FROM referrals WHERE tg_user_group_url = @v_ref_link INTO @v_usr_ref_cnt;
    IF @v_usr_ref_cnt > 0 THEN
	    SELECT u.id as u_id, 
	    		r.dt_created as dt_created_ref, r.dt_updated as dt_updated_ref, 
	    		r.dt_deleted as dt_deleted_ref, r.fk_user_id as fk_user_id_ref, 
	    		r.tg_user_group_url as tg_user_group_url_ref, r.is_active as is_active_ref, 
	    		p.dt_created as dt_created_prom, p.dt_updated as dt_updated_prom, 
	    		p.dt_deleted as dt_deleted_prom, p.fk_user_id as fk_user_id_prom, 
	    		p.tg_user_group_url as tg_user_group_url_prom, p.referral_points as referral_points_prom,
	            'success' as `status`,
	            'retreived promotor info' as info,
	            @v_user_id as promotor_user_id,
	            @v_pts_earned as promotor_pts_earned,
	            @v_usr_lost_cnt as promotor_pts_lost,
                @v_usr_ref_cnt as promotor_ref_cnt,
	            @v_ref_link as promotor_ref_link,
	            p_tg_user_id as tg_user_id_inp,
	            p_start_idx as start_idx_inp,
	            p_count as count_inp,
	            p_desc as desc_inp
	        FROM users u
	        -- INNER JOIN referrals r
	        --     ON u.id = r.fk_user_id
	        INNER JOIN promotors p 
	            ON u.id = p.fk_user_id
            INNER JOIN referrals r
                ON r.tg_user_group_url = p.tg_user_group_url
	        -- WHERE p.tg_user_group_url = @v_ref_link
	        WHERE u.id = @v_user_id
	        ORDER BY 
	            r.is_active ASC,
	            u.dt_created * (CASE WHEN p_desc THEN -1 ELSE 1 END)
	        LIMIT p_start_idx, p_count;
    ELSE
	    SELECT u.id as u_id, 
	    		p.dt_created as dt_created_prom, p.dt_updated as dt_updated_prom, 
	    		p.dt_deleted as dt_deleted_prom, p.fk_user_id as fk_user_id_prom, 
	    		p.tg_user_group_url as tg_user_group_url_prom, p.referral_points as referral_points_prom,
	            'success' as `status`,
	            'retreived promotor info' as info,
	            @v_user_id as promotor_user_id,
	            @v_pts_earned as promotor_pts_earned,
	            @v_usr_lost_cnt as promotor_pts_lost,
                @v_usr_ref_cnt as promotor_ref_cnt,
	            @v_ref_link as promotor_ref_link,
	            p_tg_user_id as tg_user_id_inp,
	            p_start_idx as start_idx_inp,
	            p_count as count_inp,
	            p_desc as desc_inp
	        FROM users u
	        INNER JOIN promotors p 
	            ON u.id = p.fk_user_id
	        WHERE u.id = @v_user_id
	        ORDER BY 
	            u.dt_created * (CASE WHEN p_desc THEN -1 ELSE 1 END)
	        LIMIT p_start_idx, p_count;
    END IF;
END 
$$ DELIMITER ;

-- # '/show_leaders'
DELIMITER $$
DROP PROCEDURE IF EXISTS GET_LEADER_BOARD;
CREATE PROCEDURE `GET_LEADER_BOARD`(
    IN p_start_idx INT(10),
    IN p_count INT(10),
    IN p_desc BOOLEAN
	)
BEGIN
    SELECT u.*, p.*,
            'success' as `status`,
            'retreived leader board' as info,
            p_start_idx as start_idx_inp,
            p_count as count_inp,
            p_desc as desc_inp
        FROM users u
        INNER JOIN promotors p
            ON u.id = p.fk_user_id
        ORDER BY u.dt_created * (CASE WHEN p_desc THEN -1 ELSE 1 END) 
        LIMIT p_start_idx, p_count;

    -- IF p_desc THEN
    --     SELECT u.*, p.* 
    --         FROM users u
    --         INNER JOIN promotors p
    --             ON u.id = p.fk_user_id
    --         ORDER BY u.dt_created DESC
    --         LIMIT p_start_idx, p_count    
    -- ELSE
    --     SELECT u.*, p.* 
    --         FROM users u
    --         INNER JOIN promotors p
    --             ON u.id = p.fk_user_id
    --         ORDER BY u.dt_created ASC
    --         LIMIT p_start_idx, p_count
    -- END IF;
END 
$$ DELIMITER ;

-- DELIMITER $$
-- DROP PROCEDURE IF EXISTS USER_JOIN_EVENT;
-- CREATE PROCEDURE `USER_JOIN_EVENT`(
--     IN p_tg_user_id VARCHAR(40), -- '581475171'
-- 	IN p_tg_user_at VARCHAR(1024), -- '@whatever'
-- 	IN p_tg_user_handle VARCHAR(1024), -- 'my handle'
--     IN p_tg_chat_id VARCHAR(40), -- '-1002003863532'
--     IN p_is_join BOOLEAN,
-- 	IN p_tg_user_group_url VARCHAR(1024) -- 't.me/<custom-link>' when join | '-1' when user leaves 
-- 	)
-- BEGIN
-- 	-- validate: tg_user_id exists (updates 'users.tg_user_at' if needed)
-- 	IF NOT valid_tg_user(p_tg_user_id, p_tg_user_at) THEN
-- 		-- add to users table
-- 		INSERT INTO users (
-- 				tg_user_id,
-- 				tg_user_at,
-- 				tg_user_handle
-- 			) VALUES (
-- 				p_tg_user_id,
-- 				p_tg_user_at,
-- 				p_tg_user_handle
-- 			);

-- 		-- get new user id
-- 		-- SELECT LAST_INSERT_ID() into @new_usr_id;
--     END IF;
    
--     -- get id of this tg user
--     SELECT id FROM users WHERE tg_user_id = p_tg_user_id INTO @v_user_id;

--     -- fail: if chat_id|ref_link combo does not exist in promotors table
--     IF NOT valid_tg_user_group_url_prom(p_tg_chat_id, p_tg_user_group_url) THEN
--         SELECT 'failed' as `status`, 
--                 'invalid chat_id|ref_link for join' as info, 
--                 @v_user_id as user_id_ref,
--                 -- @v_valid_usr_ref as valid_usr_ref,
--                 p_tg_user_id as tg_user_id_inp,
--                 p_tg_user_at as tg_user_at_inp,
--                 p_tg_user_handle as tg_user_handle_inp,
--                 p_tg_chat_id as tg_chat_id_inp,
--                 p_is_join as is_join_inp,
--                 p_tg_user_group_url as tg_user_group_url_inp;
--     ELSE

--         SELECT id FROM referrals 
--             WHERE fk_user_id = @v_user_id 
--                 AND tg_chat_id = p_tg_chat_id
--                 AND tg_user_group_url = p_tg_user_group_url
--             INTO @v_ref_id;
--         IF @v_ref_id IS NULL THEN -- found no user_id|chat_id|ref_link combo
--             -- add to referrals table 
--             --  w/ promotors id bound to chat_id|invite_link combo in promotors table
--             SELECT id FROM promotors 
--                 WHERE tg_chat_id = p_tg_chat_id 
--                     AND tg_user_group_url = p_tg_user_group_url 
--                 INTO @v_fk_user_prom_id;
--             INSERT INTO referrals (
--                     fk_user_id,
--                     fk_user_prom_id,
--                     tg_chat_id,
--                     tg_user_group_url
--                 ) VALUES (
--                     @v_user_id,
--                     @v_fk_user_prom_id,
--                     p_tg_chat_id,
--                     p_tg_user_group_url
--                 );
--         END IF;

--         SELECT id FROM referrals 
--             WHERE fk_user_id = @v_user_id 
--                 AND tg_chat_id = p_tg_chat_id
--                 AND tg_user_group_url = p_tg_user_group_url
--             INTO @v_ref_id;
--         SELECT is_active FROM referrals where id = @v_ref_id INTO @v_is_active;
--         IF @v_is_active THEN
--             SELECT 'failed' as `status`,
--                     'tg_user_id is_active already' as info, 
--                     @v_user_id as user_id_ref,
--                     @v_valid_usr_ref as valid_usr_ref,
--                     p_tg_user_id as tg_user_id_inp,
--                     p_tg_user_at as tg_user_at_inp,
--                     p_tg_user_handle as tg_user_handle_inp,
--                     p_tg_chat_id as tg_chat_id_inp,
--                     p_is_join as is_join_inp,
--                     p_tg_user_group_url as tg_user_group_url_inp;
--         ELSE
--             -- set user is_active status for this ref_id: TRUE = currently in the group, FALSE = has left the group
--             UPDATE referrals SET dt_updated = NOW(), is_active = 1 WHERE id = @v_ref_id;

--             -- calc & set promotor's points (increment|decrement)
--             SELECT referral_points FROM promotors WHERE tg_chat_id = p_tg_chat_id INTO @v_OG_pts_prom;
--             SELECT id FROM promotors 
--                 WHERE tg_user_group_url = p_tg_user_group_url
--                     AND tg_chat_id = p_tg_chat_id
--                 INTO @v_usr_prom_id;
--             UPDATE promotors 
--                 SET dt_updated = NOW(), 
--                     referral_points = CASE 
--                         WHEN p_is_join = 1 THEN referral_points + 1
--                         WHEN p_is_join = 0 AND referral_points > 0 THEN referral_points - 1
--                         ELSE referral_points
--                     END
--                 WHERE id = @v_usr_prom_id;

--             -- return
--             SELECT u.id as u_id, u.tg_user_id, u.tg_user_at, u.tg_user_handle, 
--                     r.id as r_id, r.fk_user_id as fk_user_id_ref, r.fk_user_prom_id as fk_user_prom_id_ref, r.tg_user_group_url as tg_user_group_url_ref, r.is_active as new_is_active,
--                     p.id as p_id, p.fk_user_id as fk_user_id_prom, p.tg_user_group_url as tg_user_group_url_prom, p.referral_points as new_total_pts,
--                     'success' as `status`,
--                     'updated referral is_active status & promotor ref_pts' as info,
--                     @v_user_id as user_id_ref,
--                     @v_valid_usr_ref as valid_usr_ref,
--                     @v_fk_user_prom_id as fk_user_prom_id,
--                     @v_tg_user_group_url_ref as ref_tg_user_group_url,
--                     @v_ref_id as ref_id,
--                     @v_OG_pts_prom as OG_pts,
--                     p_tg_user_id as tg_user_id_inp,
--                     p_tg_user_at as tg_user_at_inp,
--                     p_tg_user_handle as tg_user_handle_inp,
--                     p_tg_chat_id as tg_chat_id_inp,
--                     p_is_join as is_join_inp,
--                     p_tg_user_group_url as tg_user_group_url_inp
--                 FROM referrals r
--                 INNER JOIN users u
--                     ON u.id = r.fk_user_id
--                 INNER JOIN promotors p
--                     ON p.tg_user_group_url = r.tg_user_group_url
--                 WHERE r.id = @v_ref_id;
--         END IF;
--     END IF;
-- END 
-- $$ DELIMITER ;

-- # '/aux_referral_event'
DELIMITER $$
DROP PROCEDURE IF EXISTS EXE_REFERRAL_EVENT;
CREATE PROCEDURE `EXE_REFERRAL_EVENT`(
    IN p_tg_user_id VARCHAR(40), -- '581475171'
	IN p_tg_user_at VARCHAR(1024), -- '@whatever'
	IN p_tg_user_handle VARCHAR(1024), -- 'my handle'
    IN p_tg_chat_id VARCHAR(40), -- '-1002003863532'
    -- IN p_is_join INT(11),
    IN p_is_join BOOLEAN,
	IN p_tg_user_group_url VARCHAR(1024) -- 't.me/<custom-link>' when join | '-1' when user leaves 
	)
BEGIN
	-- -- fail: if tg_user_at is taken
	-- IF valid_tg_user_at(p_tg_user_at) THEN
	-- 	SELECT 'failed' as `status`, 
	-- 			'user already exists; contact support' as info, 
	-- 			p_tg_user_id as tg_user_id_inp,
	-- 			p_tg_user_at as tg_user_at_inp;

	-- validate: tg_user_id exists (updates 'users.tg_user_at' if needed)
	IF NOT valid_tg_user(p_tg_user_id, p_tg_user_at) THEN
		-- add to users table
		INSERT INTO users (
				tg_user_id,
				tg_user_at,
				tg_user_handle
			) VALUES (
				p_tg_user_id,
				p_tg_user_at,
				p_tg_user_handle
			);

		-- get new user id
		-- SELECT LAST_INSERT_ID() into @new_usr_id;
    END IF;

    -- get users table id from this tg user id
    SELECT id FROM users WHERE tg_user_id = p_tg_user_id INTO @v_user_id;

    -- check: user_id|chat_id combo exists in user_referrels
    -- SELECT valid_tg_user_referral(@v_user_id, p_tg_chat_id, p_tg_user_group_url) INTO @v_valid_usr_ref;
    SELECT valid_tg_user_referral(@v_user_id, p_tg_chat_id) INTO @v_valid_usr_ref;
    
    -- fail: if user is leaving the group WITHOUT an existing referrals entry
    IF NOT p_is_join AND NOT @v_valid_usr_ref THEN
    -- IF p_is_join = 0 AND NOT @v_valid_usr_ref THEN
		SELECT 'failed' as `status`,
				'unknown user leaving group' as info, 
                @v_user_id as user_id_ref,
                @v_valid_usr_ref as valid_usr_ref,
                p_tg_user_id as tg_user_id_inp,
                p_tg_user_at as tg_user_at_inp,
                p_tg_user_handle as tg_user_handle_inp,
                p_tg_chat_id as tg_chat_id_inp,
                p_is_join as is_join_inp,
                p_tg_user_group_url as tg_user_group_url_inp;
    
    -- NOTE: as this point...
    --  if joining (ie. p_is_join == true)
    --      then p_tg_user_group_url (ref_link) should be a valid url stored in promotors table
    --  HENCE fail: if chat_id|ref_link combo does not exist in promotors table
    ELSEIF p_is_join AND NOT valid_tg_user_group_url_prom(p_tg_chat_id, p_tg_user_group_url) THEN
        SELECT 'failed' as `status`, 
                'invalid chat_id|ref_link for join' as info, 
                @v_user_id as user_id_ref,
                @v_valid_usr_ref as valid_usr_ref,
                p_tg_user_id as tg_user_id_inp,
                p_tg_user_at as tg_user_at_inp,
                p_tg_user_handle as tg_user_handle_inp,
                p_tg_chat_id as tg_chat_id_inp,
                p_is_join as is_join_inp,
                p_tg_user_group_url as tg_user_group_url_inp;
    ELSE
        -- if join, validate: user_id|chat_id combo indeed exists in referrals table
        --  NOTE: confirmed 'p_tg_user_group_url' exists in promotors table above
        IF p_is_join AND NOT @v_valid_usr_ref THEN
            -- add to referrals table 
            --  w/ promotors id bound to chat_id|invite_link combo in promotors table
            SELECT id FROM promotors 
                WHERE tg_chat_id = p_tg_chat_id 
                    AND tg_user_group_url = p_tg_user_group_url 
                INTO @v_usr_prom_id;
            INSERT INTO referrals (
                    fk_user_id,
                    fk_user_prom_id,
                    tg_chat_id,
                    tg_user_group_url
                ) VALUES (
                    @v_user_id,
                    @v_usr_prom_id,
                    p_tg_chat_id,
                    p_tg_user_group_url
                );
        END IF;

        -- NOTE: at this point '@v_user_id' indeed exists (either joining|leaving)
        --  w/ a valid 'tg_user_group_url' entry, in 'referrals' & 'promotors' table

        -- get ref_link & ref_id bound to this user_id (tg_user_id input)
        --  for user user_id|chat_id combo
        --  NOTE: user_referreals - > id:fk_user_id+tg_chat_id == 1:1
        SELECT id FROM referrals 
            WHERE fk_user_id = @v_user_id 
                AND tg_chat_id = p_tg_chat_id 
            INTO @v_ref_id;
        SELECT tg_user_group_url FROM referrals
            WHERE id = @v_ref_id
            INTO @v_tg_user_group_url_ref;

        -- fail: if no status change would occur (hence no promotor points update either)
        SELECT is_active FROM referrals WHERE id = @v_ref_id INTO @v_OG_is_active_ref;
        IF @v_OG_is_active_ref = p_is_join THEN
            SELECT 'failed' as `status`, 
                    'is_active = p_is_join, no update exes' as info, 
                    @v_user_id as user_id_ref,
                    @v_valid_usr_ref as valid_usr_ref,
                    @v_ref_id as ref_id,
                    @v_tg_user_group_url_ref as tg_user_group_url_ref,
                    @v_OG_is_active_ref as OG_is_active_ref,
                    p_tg_user_id as tg_user_id_inp,
                    p_tg_user_at as tg_user_at_inp,
                    p_tg_user_handle as tg_user_handle_inp,
                    p_tg_chat_id as tg_chat_id_inp,
                    p_is_join as is_join_inp,
                    p_tg_user_group_url as tg_user_group_url_inp;
        ELSE
            -- set user is_active status for this ref_id: TRUE = currently in the group, FALSE = has left the group
            UPDATE referrals SET dt_updated = NOW(), is_active = p_is_join WHERE id = @v_ref_id;

            -- calc & set promotor's points (increment|decrement)
            SELECT referral_points FROM promotors WHERE tg_chat_id = p_tg_chat_id INTO @v_OG_pts_prom;
            SELECT id FROM promotors 
                WHERE tg_chat_id = p_tg_chat_id 
                    AND tg_user_group_url = @v_tg_user_group_url_ref
                INTO @v_usr_prom_id;
            UPDATE promotors 
                SET dt_updated = NOW(), 
                    referral_points = CASE 
                        WHEN p_is_join = 1 THEN referral_points + 1
                        WHEN p_is_join = 0 AND referral_points > 0 THEN referral_points - 1
                        ELSE referral_points
                    END
                WHERE id = @v_usr_prom_id;
            -- SELECT referral_points FROM promotors WHERE tg_user_group_url = p_tg_user_group_url INTO @v_pts;
            -- IF p_is_join THEN -- inc points
            --     -- SET @v_pts = @v_pts + 1;
            --     -- update user points calc'd in promotors
            --     UPDATE promotors SET referral_points = @v_pts + 1 WHERE tg_user_group_url = p_tg_user_group_url;
            -- ELSEIF @v_pts > 0 THEN -- decr points only if above 0
            --     -- SET @v_pts = @v_pts - 1;
            --     -- update user points calc'd in promotors
            --     UPDATE promotors SET referral_points = @v_pts -1 WHERE tg_user_group_url = p_tg_user_group_url;
            -- END IF;

            -- return
            SELECT u.id as u_id, u.tg_user_id, u.tg_user_at, u.tg_user_handle, 
                    r.id as r_id, r.fk_user_id as fk_user_id_ref, r.fk_user_prom_id as fk_user_prom_id_ref, r.tg_user_group_url as tg_user_group_url_ref, r.is_active as new_is_active,
                    p.id as p_id, p.fk_user_id as fk_user_id_prom, p.tg_user_group_url as tg_user_group_url_prom, p.referral_points as new_total_pts,
                    'success' as `status`,
                    'updated referral is_active status & promotor ref_pts' as info,
                    @v_user_id as user_id_ref,
                    @v_valid_usr_ref as valid_usr_ref,
                    @v_ref_id as ref_id,
                    @v_tg_user_group_url_ref as ref_tg_user_group_url,
                    @v_OG_is_active_ref as OG_is_active_ref,
                    @v_OG_pts_prom as OG_pts_prom,
                    @v_usr_prom_id as usr_prom_id,
                    p_tg_user_id as tg_user_id_inp,
                    p_tg_user_at as tg_user_at_inp,
                    p_tg_user_handle as tg_user_handle_inp,
                    p_tg_chat_id as tg_chat_id_inp,
                    p_is_join as is_join_inp,
                    p_tg_user_group_url as tg_user_group_url_inp
                FROM referrals r
                INNER JOIN users u
                    ON u.id = r.fk_user_id
                INNER JOIN promotors p
                    ON p.tg_user_group_url = r.tg_user_group_url
                WHERE r.id = @v_ref_id;
            -- SELECT COUNT(*)
            --     FROM referrals r
            --     INNER JOIN users u
            --         ON u.id = r.fk_user_id
            --     INNER JOIN promotors p
            --         ON p.tg_user_group_url = r.tg_user_group_url
            --     WHERE r.id = @v_ref_id
            --     INTO @v_ret_cnt;
            -- IF @v_ret_cnt = 0 THEN
            --     SELECT 'failed' as `status`,
            --             'proc exe returned 0 rows, return inp & vars' as info,
            --             @v_user_id as user_id_ref,
            --             @v_valid_usr_ref as valid_usr_ref,
            --             @v_fk_user_prom_id as fk_user_prom_id,
            --             @v_tg_user_group_url_ref as ref_tg_user_group_url,
            --             @v_ref_id as ref_id,
            --             @v_OG_pts_prom as OG_pts,
            --             p_tg_user_id as tg_user_id_inp,
            --             p_tg_user_at as tg_user_at_inp,
            --             p_tg_user_handle as tg_user_handle_inp,
            --             p_tg_chat_id as tg_chat_id_inp,
            --             p_is_join as is_join_inp,
            --             p_tg_user_group_url as tg_user_group_url_inp;
            -- ELSE
            --     SELECT u.id as u_id, u.tg_user_id, u.tg_user_at, u.tg_user_handle, 
            --             r.id as r_id, r.fk_user_id as fk_user_id_ref, r.fk_user_prom_id as fk_user_prom_id_ref, r.tg_user_group_url as tg_user_group_url_ref, r.is_active as new_is_active,
            --             p.id as p_id, p.fk_user_id as fk_user_id_prom, p.tg_user_group_url as tg_user_group_url_prom, p.referral_points as new_total_pts,
            --             'success' as `status`,
            --             'updated referral is_active status & promotor ref_pts' as info,
            --             @v_user_id as user_id_ref,
            --             @v_valid_usr_ref as valid_usr_ref,
            --             @v_fk_user_prom_id as fk_user_prom_id,
            --             @v_tg_user_group_url_ref as ref_tg_user_group_url,
            --             @v_ref_id as ref_id,
            --             @v_OG_pts_prom as OG_pts,
            --             p_tg_user_id as tg_user_id_inp,
            --             p_tg_user_at as tg_user_at_inp,
            --             p_tg_user_handle as tg_user_handle_inp,
            --             p_tg_chat_id as tg_chat_id_inp,
            --             p_is_join as is_join_inp,
            --             p_tg_user_group_url as tg_user_group_url_inp
            --         FROM referrals r
            --         INNER JOIN users u
            --             ON u.id = r.fk_user_id
            --         INNER JOIN promotors p
            --             ON p.tg_user_group_url = r.tg_user_group_url
            --         WHERE r.id = @v_ref_id;
            -- END IF;
        END IF;
    END IF;
END 
$$ DELIMITER ;

-- # '/gen_ref_link'
DELIMITER $$
DROP PROCEDURE IF EXISTS ADD_TG_SOWL_PROMOTOR;
CREATE PROCEDURE `ADD_TG_SOWL_PROMOTOR`(
    IN p_tg_user_id VARCHAR(40), -- '581475171'
	IN p_tg_user_at VARCHAR(1024), -- '@whatever'
	IN p_tg_user_handle VARCHAR(1024), -- 'my handle'
    IN p_tg_chat_id VARCHAR(40), -- '-1002003863532'
	IN p_tg_user_group_url VARCHAR(1024) -- 't.me/<custom-link>'
    -- IN p_wallet_address VARCHAR(255),
    -- IN p_tw_conf_url VARCHAR(1024),
	-- IN p_tw_conf_id VARCHAR(40),
	-- IN p_tw_user_at VARCHAR(255)
	)
BEGIN
	-- -- fail: if tg_user_at is taken
	-- IF valid_tg_user_at(p_tg_user_at) THEN
	-- 	SELECT 'failed' as `status`, 
	-- 			'user already exists; contact support' as info, 
	-- 			p_tg_user_id as tg_user_id_inp,
	-- 			p_tg_user_at as tg_user_at_inp;

	-- validate: tg_user_id exists taken (updates 'users.tg_user_at' if needed)
	IF NOT valid_tg_user(p_tg_user_id, p_tg_user_at) THEN
		-- add to users table
		INSERT INTO users (
				tg_user_id,
				tg_user_at,
				tg_user_handle
			) VALUES (
				p_tg_user_id,
				p_tg_user_at,
				p_tg_user_handle
			);

		-- get new user id
		-- SELECT LAST_INSERT_ID() into @new_usr_id;
    END IF;

    -- get users table id from this tg user id
    SELECT id FROM users WHERE tg_user_id = p_tg_user_id INTO @v_user_id;

    -- fail: user promotor already exists 
    IF valid_tg_user_promotor(@v_user_id, p_tg_chat_id) THEN
		SELECT u.id as u_id, u.tg_user_id, u.tg_user_at, u.tg_user_handle, 
                p.id as p_id, p.tg_chat_id, p.tg_user_group_url as OG_tg_user_group_url,
				'failed' as `status`, 
				'promotor already exists' as info, 
				p_tg_user_id as tg_user_id_inp,
				p_tg_user_at as tg_user_at_inp,
                p_tg_user_handle as tg_user_handle_inp,
                p_tg_chat_id as tg_chat_id_inp,
                p_tg_user_group_url as tg_user_group_url_inp
            FROM promotors p
            INNER JOIN users u
                ON u.id = p.fk_user_id
			WHERE p.fk_user_id = @v_user_id;
    ELSE
		-- add to promotors table
		INSERT INTO promotors (
				fk_user_id,
                tg_chat_id,
				tg_user_group_url
			) VALUES (
				@v_user_id,
                p_tg_chat_id,
				p_tg_user_group_url
			);
		-- get new promotors id
		SELECT LAST_INSERT_ID() into @new_usr_promotor_id;

		-- return
		SELECT u.id as u_id, u.tg_user_id, u.tg_user_at, u.tg_user_handle, 
                p.id as p_id, p.fk_user_id, p.tg_chat_id, p.tg_user_group_url as new_tg_user_group_url,
				'success' as `status`,
				'added new user promotor' as info,
				@v_user_id as user_id,
                @new_usr_promotor_id as user_promotor_id,
				p_tg_user_id as tg_user_id_inp,
				p_tg_user_at as tg_user_at_inp,
				p_tg_user_handle as tg_user_handle_inp,
                p_tg_chat_id as tg_chat_id_inp,
				p_tg_user_group_url as tg_user_group_url_inp
            FROM promotors p
            INNER JOIN users u
                ON u.id = p.fk_user_id
			WHERE p.id = @new_usr_promotor_id;
    END IF;
END 
$$ DELIMITER ;

-- #================================================================# --
-- # SUPPORT FUNCTIONS - SOWL
-- #================================================================# --
DELIMITER $$
drop FUNCTION if exists valid_tg_user_group_url_prom; -- setup
CREATE FUNCTION `valid_tg_user_group_url_prom`(
		p_tg_chat_id VARCHAR(40),
        p_tg_user_group_url VARCHAR(1024)) RETURNS BOOLEAN
    READS SQL DATA
    DETERMINISTIC
BEGIN
	-- check if user_id exits yet
    SELECT COUNT(*) FROM promotors WHERE tg_chat_id = p_tg_chat_id AND tg_user_group_url = p_tg_user_group_url INTO @v_cnt;
	IF @v_cnt > 0 THEN -- yes exists
		RETURN TRUE; 
	ELSE -- does not exist
		RETURN FALSE;
	END IF;
END 
$$ DELIMITER ;

DELIMITER $$
drop FUNCTION if exists valid_tg_user_promotor; -- setup
CREATE FUNCTION `valid_tg_user_promotor`(
		p_user_id VARCHAR(40),
        p_tg_chat_id VARCHAR(40)) RETURNS BOOLEAN
    READS SQL DATA
    DETERMINISTIC
BEGIN
	-- check if user_id exits yet
    SELECT COUNT(*) FROM promotors WHERE fk_user_id = p_user_id AND tg_chat_id = p_tg_chat_id INTO @v_cnt;
	IF @v_cnt > 0 THEN -- yes exists
		RETURN TRUE; 
	ELSE -- does not exist
		RETURN FALSE;
	END IF;
END 
$$ DELIMITER ;

DELIMITER $$
drop FUNCTION if exists valid_tg_user_referral; -- setup
CREATE FUNCTION `valid_tg_user_referral`(
		p_user_id VARCHAR(40),
        p_tg_chat_id VARCHAR(40)) RETURNS BOOLEAN
        -- p_tg_chat_id VARCHAR(40),
        -- p_tg_user_group_url VARCHAR(1024)) RETURNS BOOLEAN
    READS SQL DATA
    DETERMINISTIC
BEGIN
	-- check if user_id exits yet
	SELECT COUNT(*) FROM referrals 
        WHERE fk_user_id = p_user_id 
            AND tg_chat_id = p_tg_chat_id
            -- AND tg_user_group_url = p_tg_user_group_url
        INTO @v_cnt;
	IF @v_cnt > 0 THEN -- yes exists
		RETURN TRUE; 
	ELSE -- does not exist
		RETURN FALSE;
	END IF;
END 
$$ DELIMITER ;

DELIMITER $$
drop FUNCTION if exists valid_tg_user_at; -- setup
CREATE FUNCTION `valid_tg_user_at`(
		p_tg_user_at VARCHAR(40)) RETURNS BOOLEAN
    READS SQL DATA
    DETERMINISTIC
BEGIN
	-- check if user_id exits yet
	SELECT COUNT(*) FROM users WHERE tg_user_at = p_tg_user_at INTO @v_cnt;
	IF @v_cnt > 0 THEN -- yes exists
		RETURN TRUE; 
	ELSE -- does not exist
		RETURN FALSE;
	END IF;
END 
$$ DELIMITER ;

DELIMITER $$
drop FUNCTION if exists valid_tg_user; -- setup
CREATE FUNCTION `valid_tg_user`(
		p_tg_user_id VARCHAR(40),
		p_tg_user_at VARCHAR(40)) RETURNS BOOLEAN
    READS SQL DATA
    DETERMINISTIC
BEGIN
	-- check if user_id exits yet
	SELECT COUNT(*) FROM users WHERE tg_user_id = p_tg_user_id INTO @v_cnt;
	IF @v_cnt > 0 THEN -- yes exists
		-- check if user_id / user_at comnbo exists
		--	if not, update user_at for this user_id
		SELECT COUNT(*) 
			FROM users 
			WHERE tg_user_at = p_tg_user_at 
				AND tg_user_id = p_tg_user_id 
			INTO @v_found_match;
		IF @v_found_match = 0 THEN -- combo w/ user_at NOT found
			-- get support variables
			SELECT id FROM users where tg_user_id = p_tg_user_id INTO @v_user_id;
			SELECT tg_user_at FROM users where id = @v_user_id INTO @v_prev_tg_user_at;
			
			-- update existing user with new p_tg_user_at
			UPDATE users 
				SET tg_user_at = p_tg_user_at,
					dt_updated = NOW()
				WHERE tg_user_id = p_tg_user_id;

			-- log tg_user_at change in log_tg_user_at_changes
			INSERT INTO log_tg_user_at_changes (
					fk_user_id,
					tg_user_id_const,
					tg_user_at_prev,
					tg_user_at_new
				) VALUES (
					@v_user_id,
					p_tg_user_id,
					@v_prev_tg_user_at,
					p_tg_user_at
				);
		END IF;
		RETURN TRUE; 
	ELSE -- does not exist
		RETURN FALSE;
	END IF;
END 
$$ DELIMITER ;