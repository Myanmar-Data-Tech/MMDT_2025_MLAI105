import pandas as pd
import numpy as np
import os
import time
from datetime import datetime

import data_preprocessing as dp
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (confusion_matrix, classification_report, 
                           accuracy_score, precision_recall_fscore_support)

import tensorflow as tf

import matplotlib.pyplot as plt
import seaborn as sns

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ClassificationModelTrainer:
    def __init__(self, data_path='./data/MMNames_clean.csv'):
        """Initialize the trainer with data loading and preprocessing"""
        self.data_path = data_path
        self.load_and_prepare_data()
        
    def load_and_prepare_data(self):
        """Load and preprocess the data"""
        print("Loading and preparing data...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for file: {self.data_path}")
        
        # Check if file exists
        if not os.path.exists(self.data_path):
            print(f"File not found at: {self.data_path}")
            print("Available files in current directory:")
            for item in os.listdir('.'):
                print(f"  {item}")
            if os.path.exists('./data'):
                print("Files in ./data directory:")
                for item in os.listdir('./data'):
                    print(f"  ./data/{item}")
            raise FileNotFoundError(f"Could not find {self.data_path}")
        
        # Load data
        df = pd.read_csv(self.data_path)
        
        # Preprocess target first (before textinput processing)
        df = dp.preprocess_category(df, 'SR_Name')
        self.num_classes = len(df['SR_Name'].unique())
        self.y = df['SR_Name'].values  # Extract target before feature processing
        
        # Preprocess features using textinput (returns numpy array, not DataFrame)
        self.X = dp.preprocess_textinput(df, 'name')
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.3, random_state=42
        )
        
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        print(f"Data prepared: Train shape {self.X_train.shape}, Test shape {self.X_test.shape}")
        print(f"Number of classes: {self.num_classes}")
        print(f"Feature reduction: One-hot encoding → CountVectorizer (max_features=5000)")
        print(f"Expected parameter reduction: ~416K → ~160K parameters")
    
    def create_classification_model(self, layers):
        """Create a neural network model with specified layer configuration"""
        model = tf.keras.Sequential()
        
        # Add first hidden layer with input shape
        model.add(tf.keras.layers.Dense(layers[0], activation='relu', input_shape=(self.X_train.shape[1],)))
        
        # Add remaining hidden layers
        for neurons in layers[1:-1]:
            model.add(tf.keras.layers.Dense(neurons, activation='relu'))
        
        # Add output layer (softmax for classification)
        model.add(tf.keras.layers.Dense(layers[-1], activation='softmax'))
        
        model.compile(optimizer='adam', 
                     loss='sparse_categorical_crossentropy', 
                     metrics=['accuracy'])
        return model
    
    def save_model_summary(self, model, save_path):
        """Save model summary to text file"""
        with open(os.path.join(save_path, 'model_summary.txt'), 'w') as f:
            model.summary(print_fn=lambda x: f.write(x + '\n'))
            f.write(f"\nTotal Parameters: {model.count_params():,}\n")
    
    def plot_training_history(self, history, save_path):
        """Plot and save training history (loss and accuracy)"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Training and Validation Loss
        axes[0, 0].plot(history.history['loss'], label='Training Loss', linewidth=2)
        axes[0, 0].plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].set_title('Training and Validation Loss Over Epochs')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Training and Validation Accuracy
        axes[0, 1].plot(history.history['accuracy'], label='Training Accuracy', linewidth=2)
        axes[0, 1].plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].set_title('Training and Validation Accuracy Over Epochs')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Loss (Log Scale)
        axes[1, 0].plot(history.history['loss'], label='Training Loss (Log Scale)', linewidth=2)
        axes[1, 0].plot(history.history['val_loss'], label='Validation Loss (Log Scale)', linewidth=2)
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Loss (Log Scale)')
        axes[1, 0].set_title('Training and Validation Loss Over Epochs (Log Scale)')
        axes[1, 0].set_yscale('log')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Overfitting/Underfitting Analysis
        train_loss = history.history['loss']
        val_loss = history.history['val_loss']
        train_acc = history.history['accuracy']
        val_acc = history.history['val_accuracy']
        
        # Calculate overfitting indicators
        final_train_loss = train_loss[-1]
        final_val_loss = val_loss[-1]
        final_train_acc = train_acc[-1]
        final_val_acc = val_acc[-1]
        
        loss_gap = final_val_loss - final_train_loss
        acc_gap = final_train_acc - final_val_acc
        
        # Create text analysis
        analysis_text = f"Final Training Loss: {final_train_loss:.4f}\n"
        analysis_text += f"Final Validation Loss: {final_val_loss:.4f}\n"
        analysis_text += f"Loss Gap: {loss_gap:.4f}\n\n"
        analysis_text += f"Final Training Accuracy: {final_train_acc:.4f}\n"
        analysis_text += f"Final Validation Accuracy: {final_val_acc:.4f}\n"
        analysis_text += f"Accuracy Gap: {acc_gap:.4f}\n\n"
        
        if loss_gap > 0.1 and acc_gap > 0.05:
            analysis_text += "Indication: OVERFITTING\n"
            analysis_text += "- Validation loss higher than training loss\n"
            analysis_text += "- Training accuracy much higher than validation"
        elif final_train_acc < 0.7 and final_val_acc < 0.7:
            analysis_text += "Indication: UNDERFITTING\n"
            analysis_text += "- Both training and validation accuracies are low"
        else:
            analysis_text += "Indication: GOOD FIT\n"
            analysis_text += "- Reasonable gap between training and validation metrics"
        
        axes[1, 1].text(0.05, 0.95, analysis_text, transform=axes[1, 1].transAxes, 
                       fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        axes[1, 1].set_title('Overfitting/Underfitting Analysis')
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, 'training_history.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_confusion_matrix(self, y_true, y_pred, save_path, dataset_name):
        """Plot and save confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=range(self.num_classes),
                   yticklabels=range(self.num_classes))
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        accuracy = accuracy_score(y_true, y_pred)

        plt.title(f'Confusion Matrix - {dataset_name} - Accuracy: {accuracy:.4f}')
        
        # # Add accuracy to the plot
        # accuracy = accuracy_score(y_true, y_pred)
        # plt.text(0.02, 0.98, f'Accuracy: {accuracy:.4f}', transform=plt.gca().transAxes,
        #         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
        #         verticalalignment='top')
        
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, f'confusion_matrix_{dataset_name.lower()}.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save confusion matrix as CSV
        cm_df = pd.DataFrame(cm, 
                           index=[f'True_{i}' for i in range(self.num_classes)],
                           columns=[f'Pred_{i}' for i in range(self.num_classes)])
        cm_df.to_csv(os.path.join(save_path, f'confusion_matrix_{dataset_name.lower()}.csv'))
        
        return cm
    
    def evaluate_model(self, model, save_path, training_time):
        """Evaluate model and save results"""
        # Predictions
        y_train_pred_proba = model.predict(self.X_train, batch_size=32, verbose=0)
        y_test_pred_proba = model.predict(self.X_test, batch_size=32, verbose=0)
        
        y_train_pred = y_train_pred_proba.argmax(axis=1)
        y_test_pred = y_test_pred_proba.argmax(axis=1)
        
        # Classification reports
        train_report = classification_report(self.y_train, y_train_pred, output_dict=True)
        test_report = classification_report(self.y_test, y_test_pred, output_dict=True)
        
        # Save classification reports
        train_report_df = pd.DataFrame(train_report).round(4).transpose()
        test_report_df = pd.DataFrame(test_report).round(4).transpose()
        
        train_report_df.to_csv(os.path.join(save_path, 'classification_report_train.csv'))
        test_report_df.to_csv(os.path.join(save_path, 'classification_report_test.csv'))
        
        # Create confusion matrices
        train_cm = self.plot_confusion_matrix(self.y_train, y_train_pred, save_path, 'Train')
        test_cm = self.plot_confusion_matrix(self.y_test, y_test_pred, save_path, 'Test')
        
        # Calculate comprehensive metrics
        train_accuracy = accuracy_score(self.y_train, y_train_pred)
        test_accuracy = accuracy_score(self.y_test, y_test_pred)
        
        train_precision, train_recall, train_f1, _ = precision_recall_fscore_support(
            self.y_train, y_train_pred, average='weighted'
        )
        test_precision, test_recall, test_f1, _ = precision_recall_fscore_support(
            self.y_test, y_test_pred, average='weighted'
        )
        
        # Compile results
        results = {
            'Train_Accuracy': train_accuracy,
            'Test_Accuracy': test_accuracy,
            'Train_Precision': train_precision,
            'Test_Precision': test_precision,
            'Train_Recall': train_recall,
            'Test_Recall': test_recall,
            'Train_F1_Score': train_f1,
            'Test_F1_Score': test_f1,
            'Training_Time': training_time
        }
        
        # Save summary results
        results_df = pd.DataFrame([results]).round(4)
        results_df.to_csv(os.path.join(save_path, 'evaluation_summary.csv'), index=False)
        
        return results, train_report_df, test_report_df
    
    def train_single_model(self, model_config, model_name):
        """Train a single model configuration"""
        print(f"\nTraining {model_name}")
        print(f"Architecture: {' -> '.join(map(str, model_config))}")
        
        # Create directory
        save_dir = os.path.join('results2', model_name)
        os.makedirs(save_dir, exist_ok=True)
        
        # Create model
        model = self.create_classification_model(model_config)
        
        # Save model summary
        self.save_model_summary(model, save_dir)
        
        # Train model
        start_time = time.time()
        history = model.fit(
            self.X_train, self.y_train,
            epochs=50,  # Fixed at 50 epochs as requested
            batch_size=32,
            validation_data=(self.X_test, self.y_test),
            verbose=1
        )
        training_time = time.time() - start_time
        
        # Save training history plots
        self.plot_training_history(history, save_dir)
        
        # Evaluate and save results
        results, train_report, test_report = self.evaluate_model(model, save_dir, training_time)
        
        # Save training history data
        history_df = pd.DataFrame(history.history)
        history_df.to_csv(os.path.join(save_dir, 'training_history.csv'), index=False)
        
        print(f"Completed {model_name}")
        print(f"Training time: {training_time:.2f} seconds")
        print(f"Test Accuracy: {results['Test_Accuracy']:.4f}")
        
        actual_total_params = model.count_params()
        print(f"Total Parameters: {actual_total_params:,}")

        return results, train_report, test_report, actual_total_params
    
    def run_all_experiments(self):
        """Run all model architectures"""
        # Model configurations - progressive layer addition
        model_configs = {
            'model1': [32, 16, self.num_classes],
            'model2': [64, 32, 16, self.num_classes],
            'model3': [128, 64, 32, 16, self.num_classes],
            'model4': [256, 128, 64, 32, 16, self.num_classes],
            'model5': [256, 128, 64, 32, self.num_classes],
            'model6': [128, 64, 32, self.num_classes],
            'model7': [64, 32, self.num_classes]
        }
        
        # Create results directory
        os.makedirs('results', exist_ok=True)
        
        # Store all results for summary
        all_results = []
        detailed_reports = {'train': [], 'test': []}
        
        # Run experiments
        for model_name, model_config in model_configs.items():
            print(f"\n{'='*60}")
            print(f"Starting experiment for {model_name}")
            print(f"Architecture: {' -> '.join(map(str, model_config))}")
            print(f"{'='*60}")
            
            try:
                results, train_report, test_report, actual_total_params = self.train_single_model(
                    model_config, model_name
                )
                
                # Store summary info
                summary_info = {
                    'Model': model_name,
                    'Architecture': ' -> '.join(map(str, model_config[:-1])) + f' -> {model_config[-1]} (softmax)',
                    'Total_Layers': len(model_config),
                    'Hidden_Layers': len(model_config) - 1,
                    'Total_Params': actual_total_params,
                    **results
                }
                all_results.append(summary_info)
                
                # Store detailed reports with model info
                train_report_with_model = train_report.copy()
                train_report_with_model['Model'] = model_name
                test_report_with_model = test_report.copy()
                test_report_with_model['Model'] = model_name
                
                detailed_reports['train'].append(train_report_with_model)
                detailed_reports['test'].append(test_report_with_model)
                
            except Exception as e:
                print(f"Error training {model_name}: {str(e)}")
                continue
        
        # Save executive summary
        self.create_executive_summary(all_results, detailed_reports)
        
        print(f"\n{'='*60}")
        print("ALL EXPERIMENTS COMPLETED!")
        print(f"{'='*60}")
        print(f"Results saved in 'results' directory")
        print(f"Executive summary saved as 'results/executive_summary.csv'")
        
        return pd.DataFrame(all_results)
    
    def create_executive_summary(self, all_results, detailed_reports):
        """Create comprehensive executive summary"""
        # Check if we have results
        if not all_results:
            print("No successful results to create summary")
            return
            
        # Main summary
        summary_df = pd.DataFrame(all_results)
        summary_df = summary_df.round(4)
        summary_df.to_csv('results2/executive_summary.csv', index=False)
        
        # Detailed classification reports
        if detailed_reports['train']:
            train_detailed = pd.concat(detailed_reports['train'], ignore_index=True)
            train_detailed.to_csv('results2/detailed_classification_report_train.csv', index=False)
        
        if detailed_reports['test']:
            test_detailed = pd.concat(detailed_reports['test'], ignore_index=True)
            test_detailed.to_csv('results2/detailed_classification_report_test.csv', index=False)
        
        # Create performance comparison chart only if we have data
        if len(summary_df) > 0:
            self.create_performance_comparison(summary_df)
        
        print(f"\nExecutive Summary Created:")
        print(f"- Main summary: results2/executive_summary.csv")
        if detailed_reports['train']:
            print(f"- Detailed train reports: results2/detailed_classification_report_train.csv")
        if detailed_reports['test']:
            print(f"- Detailed test reports: results2/detailed_classification_report_test.csv")
        if len(summary_df) > 0:
            print(f"- Performance comparison: results2/performance_comparison.png")
    
    def create_performance_comparison(self, summary_df):
        """Create performance comparison visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        models = summary_df['Model']
        
        # Accuracy comparison
        axes[0, 0].bar(models, summary_df['Train_Accuracy'], alpha=0.7, label='Train Accuracy')
        axes[0, 0].bar(models, summary_df['Test_Accuracy'], alpha=0.7, label='Test Accuracy')
        axes[0, 0].set_title('Accuracy Comparison Across Models')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # F1 Score comparison
        axes[0, 1].bar(models, summary_df['Train_F1_Score'], alpha=0.7, label='Train F1')
        axes[0, 1].bar(models, summary_df['Test_F1_Score'], alpha=0.7, label='Test F1')
        axes[0, 1].set_title('F1 Score Comparison Across Models')
        axes[0, 1].set_ylabel('F1 Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Training time comparison
        axes[1, 0].bar(models, summary_df['Training_Time'], alpha=0.7, color='orange')
        axes[1, 0].set_title('Training Time Comparison')
        axes[1, 0].set_ylabel('Training Time (seconds)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Model complexity (parameters)
        axes[1, 1].bar(models, summary_df['Total_Params'], alpha=0.7, color='green')
        axes[1, 1].set_title('Model Complexity (Total Parameters)')
        axes[1, 1].set_ylabel('Number of Parameters')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('results2/performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """Main function to run all experiments"""
    print("Starting Automated Classification Model Training Pipeline")
    print("="*60)
    
    # Initialize trainer
    trainer = ClassificationModelTrainer()
    
    # Run all experiments
    summary = trainer.run_all_experiments()
    
    # Display final summary only if we have results
    if len(summary) > 0:
        print("\nFinal Experiment Summary:")
        print(summary[['Model', 'Architecture', 'Test_Accuracy', 'Test_F1_Score', 'Training_Time']].to_string(index=False))
        
        # Find best model
        best_model_idx = summary['Test_Accuracy'].idxmax()
        best_model = summary.iloc[best_model_idx]
        
        print(f"\nBest Performing Model:")
        print(f"Model: {best_model['Model']}")
        print(f"Architecture: {best_model['Architecture']}")
        print(f"Test Accuracy: {best_model['Test_Accuracy']:.4f}")
        print(f"Test F1 Score: {best_model['Test_F1_Score']:.4f}")
        print(f"Training Time: {best_model['Training_Time']:.2f} seconds")
    else:
        print("\nNo models were successfully trained. Please check the errors above.")

if __name__ == "__main__":
    main()