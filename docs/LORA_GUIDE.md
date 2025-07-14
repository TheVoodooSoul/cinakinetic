# 🎯 LoRA Training Guide for Action Scene Generation

## What are LoRAs?

**LoRA (Low-Rank Adaptation)** allows you to train custom models for:
- **Character Consistency** → Same character across multiple action scenes
- **Fighting Styles** → Specific martial arts, boxing, combat techniques
- **Action Poses** → Custom dynamic poses and movements
- **Visual Styles** → Consistent cinematography and lighting

## 🎬 **How to Access LoRA Features**

### In the App:
1. **Main Navigation** → "🎯 LoRA Studio" 
2. **Production Studio** → "🎯 LoRA Studio" tab

### LoRA Studio Sections:
- **📚 Train New LoRA** → Create custom LoRAs
- **👥 Character Manager** → Manage consistent characters
- **🥊 Fighting Styles** → Train fighting technique LoRAs
- **📖 LoRA Library** → Manage all your LoRAs

## 🎯 **Character Consistency Workflow**

### Step 1: Create Character
1. Go to **Character Manager**
2. Click **"Add New Character"**
3. Fill in:
   - Character name (e.g., "Action Hero John")
   - Description (appearance, style)
   - Fighting style (boxing, martial arts, etc.)
   - Upload reference image

### Step 2: Train Character LoRA
1. Click **"Train LoRA"** for your character
2. Upload **15-25 high-quality images** of the same character:
   - Different poses and angles
   - Various lighting conditions
   - Include close-ups and full-body shots
   - Same character, different backgrounds OK

### Step 3: Use in Generation
1. Go to **Production Studio** → **Studio** tab
2. In **LoRA Selection**, choose your character
3. Generate scenes → character will be consistent!

## 🥊 **Fighting Style LoRAs**

### Pre-Built Styles Available:
- **Professional Boxing** (`boxingstyle`)
- **Kung Fu Martial Arts** (`kungfustyle`)
- **Mixed Martial Arts** (`mmastyle`)
- **Sword Combat** (`swordstyle`)

### Train Custom Fighting Style:
1. **Fighting Styles** → **"Create Custom Fighting Style"**
2. Upload **20-40 images** showing:
   - Specific martial art techniques
   - Various practitioners (consistency in style, not person)
   - Different poses and stances
   - Clear technique demonstration

### Usage in Prompts:
```
"epic fight scene, kungfustyle, two fighters in combat"
"boxing match, boxingstyle, powerful jab technique"
"sword duel, swordstyle, parrying and thrusting"
```

## 📊 **LoRA Training Costs (RTX 6000 Ada)**

### Character LoRA (15-25 images):
- **Time**: 15-25 minutes
- **Credits**: 50-75
- **GPU Cost**: ~$1.00

### Fighting Style LoRA (20-40 images):
- **Time**: 20-35 minutes  
- **Credits**: 75-100
- **GPU Cost**: ~$1.50

### High-Resolution Training (1024x1024):
- **Additional Time**: +50%
- **Additional Cost**: +$0.50

## 🎨 **Image Requirements for Best Results**

### Character LoRAs:
```
✅ Good Images:
- High resolution (768x768+)
- Clear face/body visibility
- Different poses and angles
- Varied lighting conditions
- Same character consistently

❌ Avoid:
- Blurry or low-resolution images
- Heavy shadows obscuring features
- Different characters mixed in
- Heavily filtered/stylized images
- Cropped faces or bodies
```

### Fighting Style LoRAs:
```
✅ Good Images:
- Clear technique demonstration
- Full body visibility
- Various martial art poses
- Different practitioners OK
- Action shots and stances

❌ Avoid:
- Static poses
- Poor technique examples
- Unclear body positioning
- Single practitioner only
- Non-martial art content
```

## 🔧 **Advanced Training Settings**

### Character LoRA Optimal Settings:
```yaml
Steps: 1000-1500
Learning Rate: 1e-4
Network Dim: 64
Network Alpha: 32
Resolution: 768x768
Batch Size: 1
```

### Fighting Style LoRA Optimal Settings:
```yaml
Steps: 1500-2000
Learning Rate: 8e-5
Network Dim: 32-48
Network Alpha: 16-24
Resolution: 768x768
Batch Size: 2
```

## 🎬 **Using LoRAs in Production**

### Single Character Scene:
1. Select character in LoRA Selection
2. Add fighting style if desired
3. Generate → consistent character with style

### Multi-Character Scene:
1. Train separate LoRAs for each character
2. Use in prompt: `"character1, character2, kungfustyle, epic fight"`
3. Adjust LoRA strengths (0.6-0.8 each)

### Character Development Across Scenes:
1. Create character LoRA
2. Generate multiple scenes with same character
3. Maintain visual consistency across action sequence
4. Export as complete storyboard

## 💡 **Pro Tips for Best Results**

### Character Consistency:
- **Use trigger words**: Include character trigger in every prompt
- **LoRA strength**: 0.7-0.9 for strong consistency
- **Combine with style**: Character + fighting style for best results

### Fighting Choreography:
- **Layer LoRAs**: Character + fighting style + pose LoRA
- **Prompt engineering**: Describe specific techniques
- **Strength balance**: Character (0.8) + Style (0.6) + Pose (0.4)

### Scene Continuity:
- **Save LoRA settings**: Document successful combinations
- **Consistent seeds**: Use same seed for similar poses
- **Batch generation**: Generate variations with same LoRAs

## 🚀 **Example Workflows**

### Epic Fight Sequence:
```
1. Train "ActionHero_John" character LoRA
2. Train "Villain_Kane" character LoRA  
3. Use "kungfustyle" fighting LoRA
4. Generate sequence:
   - Scene 1: "johnhero faces kanehero, kungfustyle, fighting stance"
   - Scene 2: "johnhero attacks kanehero, kungfustyle, punch sequence"
   - Scene 3: "kanehero blocks johnhero, kungfustyle, defensive pose"
```

### Character Development:
```
1. Create character with reference images
2. Train LoRA with 20+ varied poses
3. Generate across different scenarios:
   - "johnhero in office, dramatic lighting"
   - "johnhero fighting, kungfustyle, action scene"
   - "johnhero injured, dramatic close-up"
```

## ❓ **Troubleshooting**

### "LoRA not affecting generation":
- Check trigger word is in prompt
- Increase LoRA strength (0.8-1.0)
- Verify LoRA trained successfully

### "Character inconsistency":
- Use more training images (20-25)
- Ensure image quality is high
- Include more pose variety in training

### "Fighting style not accurate":
- Train on technique-specific images
- Use multiple fighting style references
- Adjust LoRA strength for style

### "Training failed":
- Check image formats (PNG/JPG only)
- Ensure minimum image count met
- Verify no corrupted images

## 📈 **LoRA Performance Metrics**

Your LoRA Studio tracks:
- **Usage Count**: How often each LoRA is used
- **Success Rate**: Generation success with LoRA
- **User Rating**: Quality ratings for each LoRA
- **Training Time**: Efficiency metrics

## 🎯 **Ready to Start?**

1. **Character Consistency**: Go to Character Manager → Add New Character
2. **Fighting Styles**: Go to Fighting Styles → Train Custom Style  
3. **Advanced**: Go to Train New LoRA → Custom configuration

**Your RTX 6000 Ada setup is perfect for LoRA training** - fast, high-quality results in 15-35 minutes per LoRA!

Start with a character LoRA first, then add fighting styles for the ultimate action scene consistency! 🥊🎬