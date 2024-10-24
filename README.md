# sowl_bots
sowl bots (OG referral bot)

## Features:
    1) generate a personal referal link to this TG group (TG @username required, 1 link per @username)
    2) give that link to anyone you want to refer to this TG group
    3) someone uses your personal referal link to join this TG group
    4) you will earn 1 point for each person that uses your referal link
    5) you will lose 1 point if a person who joins with your link, leaves this TG group
    6) you can view promotor info (referal link, points earned, users joined, users/points lost)

## CMDs ...
    /gen_ref_link
    /show_my_referrals
    /show_leaders
    <aux_referral_event>

## Instructions:
    1) install mysql
        - google/chatGPT
    2) install database
        $ mysql -u root
        > source ./database/schemas/sowl_db_schema.sql
        > source ./database/schemas/sowl_proc_schema.sql
    3) create bot and get secret key/token
        - TG: @botfather
    4) create/set .env file in ./src/_env
        # db access
        DB_HOST=127.0.0.1
        DB_USERNAME=dev
        DB_PASSWORD=password
        DB_DATABASE=sowl
        TG_TOKEN_SWOWL_TEST=xxxxx # @sowl_test_bot
    5) run bot
        $ python3.11 refer_bot.py

## Questions: @housing37

## *IMORTANT* 
    you DO NOT need a TG @username setup to use this bot

## GLHF!