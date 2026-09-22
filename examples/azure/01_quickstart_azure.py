"""
Azure OpenAI: Enterprise Private Deployment Swarm
==================================================
Demonstrates running a swarm using Azure OpenAI private deployments.
"""

import os
from swarmmy import Config, create_provider, run_sync


def main():
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

    if not api_key:
        print("[WARN] AZURE_OPENAI_API_KEY not found in environment.")
        print("       Running in mock demo mode for demonstration...\n")
        def backend(messages, **kwargs):
            return "Consensus: Azure OpenAI private deployment completed enterprise swarm task."
    else:
        # Example Azure deployment
        backend = create_provider(
            "azure",
            deployment="my-gpt4o-deployment",
            api_key=api_key,
            base_url=endpoint,
        )

    config = Config(agents=3, rounds=1, concurrency=3)

    task = "Formulate an enterprise data retention policy compliant with SOC-2 and HIPAA."

    print(">>> Starting Swarmmy with Azure OpenAI...")
    result = run_sync(task, backend=backend, config=config, live=True)

    print("\n" + "=" * 70)
    print("🏆 FINAL ANSWER:")
    print("=" * 70)
    print(result.answer)


if __name__ == "__main__":
    main()
