Place the fine-tuned behavior classifier checkpoint here, e.g.:

```
models/
  ccae-behavior-classifier-v1/
    config.json
    pytorch_model.bin
    tokenizer.json
    tokenizer_config.json
    vocab.txt
    labels.json
    thresholds.json
```

The `labels.json` file should contain a list of label names that matches the model's output order. `thresholds.json` is optional; if omitted, the inference code falls back to a uniform threshold of 0.4.

