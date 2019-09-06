
let guess_game ( to_guess : int) =
    (*Does the order of let statements matter?*)
    let success = ref false in
    let guess   = ref 0 in
    let count   = ref 1 in
    while not (!success) && (!count)<=6 do
        print_string ("What is your guess?\n");
        print_string ("Guesses remaining: "^(string_of_int (7-(!count)))^"\n");

        guess := int_of_string (read_line ());
        if (!guess) < to_guess
        then begin
             print_string ("Too low. Guess higher.\n");
             incr (count);
             end
        else begin if (!guess) > to_guess
                   then begin
                        print_string ("Too high. Guess lower.\n");
                        incr (count);
                        (*print_string ("Guesses remaining: "^(string_of_int (6-(!count)))^"\n");*)
                        end
                   else begin
                        success := true;
                        end
             end;
    done;
    if not (!success)
      then begin
      print_string ("Sorry, you didn't get it. My number was "^(string_of_int (to_guess))^".\n");
      end
    else begin
      print_string ("You got it in "^(string_of_int (!count))^" guesses. My number was "^(string_of_int (to_guess))^". Good job!\n");
    end
let _ = begin Random.self_init (); guess_game (Random.int (100)); end
