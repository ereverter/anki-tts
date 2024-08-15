import argparse

import tiktoken


def count_tokens(text: str) -> int:
    tokenizer = tiktoken.get_encoding("gpt2")
    tokens = tokenizer.encode(text)
    return len(tokens)


def compute_llm_pricing(
    n_input_tokens: int,
    n_output_tokens: int,
    p_input_tokens: float,
    p_output_tokens: float,
) -> float:
    input_cost = n_input_tokens * p_input_tokens
    output_cost = n_output_tokens * p_output_tokens
    total_cost = input_cost + output_cost
    return total_cost


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Token counting and LLM pricing computation"
    )
    parser.add_argument(
        "-t", "--text", type=str, required=True, help="The text to be tokenized"
    )
    parser.add_argument(
        "-not",
        "--n_output_tokens",
        type=int,
        required=True,
        help="The number of output tokens",
    )
    parser.add_argument(
        "-pit",
        "--p_input_tokens",
        type=float,
        required=True,
        help="The price per input token",
    )
    parser.add_argument(
        "-pot",
        "--p_output_tokens",
        type=float,
        required=True,
        help="The price per output token",
    )

    args = parser.parse_args()

    n_input_tokens = count_tokens(args.text)
    total_cost = compute_llm_pricing(
        n_input_tokens, args.n_output_tokens, args.p_input_tokens, args.p_output_tokens
    )

    print(f"Number of input tokens: {n_input_tokens}")
    print(f"Total cost: ${total_cost:.2f}")
