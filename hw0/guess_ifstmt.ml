
let guess_game ( to_guess : int) =
    let success = ref false in
    let guess   = ref 0 in
    let count   = ref 0 in
    while not (!success) && (!count)<6 do
        print_string ("Guesses remaining: "^(string_of_int (7-(!count)))^"\n");
        print_string ("What is your guess?\n");
        guess := int_of_string (read_line ());
        if (!guess) < to_guess then print_string ("Too low. Guess higher.\n") incr (count)
        else if (!guess) > to_guess then print_string ("Too high. Guess lower.\n") incr (count)
        else success := true;
    done;
    if not (!success) then print_string ("Sorry! Better luck next time!\n")
    else print_string ("You got it. My number was "^(string_of_int (to_guess))^". Good job!\n");;

let _ = begin Random.self_init (); guess_game (Random.int (100)); end
