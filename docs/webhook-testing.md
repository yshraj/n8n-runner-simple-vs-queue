# Webhook Performance Testing

## Install Dependencies

```powershell
pip install -r ../requirements-test.txt
```

## Quick Test (Debug)

Test webhook URL and format:
```powershell
python ../test-webhook-simple.py
```

This helps identify:
- If webhook exists (GET test)
- Correct URL format
- Correct payload format

## Run Performance Test

```powershell
python ../test-webhook-performance.py
```

Paste your webhook URL when prompted. The script will:
- Send 5, 10, and 20 parallel requests
- Measure individual and batch completion times
- Save results to `results/` folder

## Troubleshooting 404 Errors

If you get 404 errors:
1. Check if workflow is **Active** in n8n UI
2. Verify webhook path in n8n webhook node
3. Try URL without `/chat` if path is not configured
4. See `webhook-troubleshooting.md` for details

## Compare Results

```powershell
python ../compare_results.py results/file1.json results/file2.json
```

