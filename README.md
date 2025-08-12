# Family Weekly Dinner Plans

This repo stores custom weekly dinner plans for my family (some details edited out), generated from a detailed LLM prompt that encodes our family’s preferences, nutrition goals, and cooking routines.

Each week includes three LLM-generated files:
- **Grocery_List.md** – grocery list including quantities, grouped by aisle
- **Day_By_Day_Instructions.md** – quick recipes + leftover-packing notes
- **Sunday_Meal_Prep.md** – batch-prep guide with exact amounts and labeled storage

## How to Reuse
1. **Adjust `prompt-1.md`** – Replace our family’s details with yours (you can ask an LLM to help tailor it).
2. Run **`prompt-2.md`** and then **`prompt-3.md`** in sequence.  
   This will generate three `.md` files as above.
3. Use the provided Python script to convert them to PDFs:
   ```bash
   python3 md_to_pdf.py <path to generated md file>
   ```
