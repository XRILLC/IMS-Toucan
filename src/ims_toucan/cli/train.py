"""Training CLI for IMS-Toucan."""

import sys


def main():
    """Training entry point - wrapper around run_training_pipeline.py."""
    import argparse

    parser = argparse.ArgumentParser(
        description="IMS-Toucan Training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with a recipe
  toucan-train --recipe finetuning_example_simple --gpu-id 0

  # Resume training
  toucan-train --recipe nancy --resume --gpu-id 0

  # Multi-GPU training
  torchrun --standalone --nproc_per_node=4 $(which toucan-train) --recipe stage2 --gpu-id "0,1,2,3"

  # Fine-tune from checkpoint
  toucan-train --recipe my_recipe --finetune --gpu-id 0
        """
    )

    parser.add_argument(
        "recipe",
        type=str,
        help="Training recipe name (see run_training_pipeline.py for available recipes)"
    )

    parser.add_argument(
        "--gpu-id",
        type=str,
        default="0",
        help='GPU ID(s) to use (e.g., "0" or "0,1,2,3" for multi-GPU)'
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from most recent checkpoint"
    )

    parser.add_argument(
        "--resume-checkpoint",
        type=str,
        help="Resume from specific checkpoint path"
    )

    parser.add_argument(
        "--finetune",
        action="store_true",
        help="Fine-tune from checkpoint (only load model, not optimizer)"
    )

    parser.add_argument(
        "--model-save-dir",
        type=str,
        help="Custom directory to save model checkpoints"
    )

    parser.add_argument(
        "--wandb",
        action="store_true",
        help="Enable Weights & Biases logging"
    )

    parser.add_argument(
        "--wandb-resume-id",
        type=str,
        help="W&B run ID to resume"
    )

    args = parser.parse_args()

    # Import and run training pipeline
    try:
        from run_training_pipeline import pipeline_dict
    except ImportError as e:
        print(f"Error: Failed to import training pipeline: {e}", file=sys.stderr)
        print("Make sure you're running from the IMS-Toucan root directory.", file=sys.stderr)
        return 1

    # Validate recipe
    if args.recipe not in pipeline_dict:
        print(f"Error: Unknown recipe '{args.recipe}'", file=sys.stderr)
        print(f"\nAvailable recipes:", file=sys.stderr)
        for recipe_name in sorted(pipeline_dict.keys()):
            print(f"  - {recipe_name}", file=sys.stderr)
        return 1

    # Determine GPU count
    if "," in args.gpu_id:
        gpu_count = len(args.gpu_id.split(","))
    else:
        gpu_count = 1

    print(f"Starting training: {args.recipe}")
    print(f"GPUs: {args.gpu_id} (count: {gpu_count})")
    print(f"Resume: {args.resume}, Finetune: {args.finetune}")

    # Run the recipe
    try:
        pipeline_dict[args.recipe](
            gpu_id=args.gpu_id,
            resume_checkpoint=args.resume_checkpoint,
            finetune=args.finetune,
            model_dir=args.model_save_dir,
            resume=args.resume,
            use_wandb=args.wandb,
            wandb_resume_id=args.wandb_resume_id,
            gpu_count=gpu_count
        )
        return 0
    except Exception as e:
        print(f"Training failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
