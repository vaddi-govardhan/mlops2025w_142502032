import json
import torch
import torchvision.models as models
from torchvision.models import ResNet34_Weights, ResNet50_Weights, ResNet101_Weights, ResNet152_Weights

def load_model(name, device='cpu'):
    name = name.lower()
    if name == 'resnet34':
        m = models.resnet34(weights=ResNet34_Weights.IMAGENET1K_V1)
    elif name == 'resnet50':
        m = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    elif name == 'resnet101':
        m = models.resnet101(weights=ResNet101_Weights.IMAGENET1K_V1)
    elif name == 'resnet152':
        m = models.resnet152(weights=ResNet152_Weights.IMAGENET1K_V1)
    else:
        raise ValueError(f"Unsupported model: {name}")
    m.eval()
    return m.to(device)

def run_inference(model_name, device='cpu'):
    model = load_model(model_name, device=device)
    x = torch.randn(1, 3, 224, 224, device=device)
    with torch.no_grad():
        out = model(x)
    print(f"[Inference] {model_name}: output shape {out.shape}")
    return list(out.shape)

def run_grid_search(grid_file="grid.json"):
    with open(grid_file) as f:
        grid = json.load(f)
    combos = []
    for lr in grid.get("learning_rates", []):
        for opt in grid.get("optimizers", []):
            for mom in grid.get("momentum", []):
                combos.append({"lr": lr, "optimizer": opt, "momentum": mom})
    print(f"\\n[Grid Search] Total combinations: {len(combos)}")
    for i, c in enumerate(combos, 1):
        print(f"Combo {i}: {c}")
    return {"total_combinations": len(combos), "combinations": combos}

def main():
    device = "cpu"
    models_to_run = ["resnet34", "resnet50", "resnet101", "resnet152"]

    print("=== Running Inference on Pretrained ResNet Models ===")
    inference_results = []
    for m in models_to_run:
        shape = run_inference(m, device=device)
        inference_results.append({"model": m, "output_shape": shape})

    print("\\n=== Running Hyperparameter Grid Search ===")
    grid_results = run_grid_search("grid.json")

    # Save results to results.json
    results = {"inference": inference_results, "grid_search": grid_results}
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\\nSaved results to results.json")

if __name__ == "__main__":
    main()
