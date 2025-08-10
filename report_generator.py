import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import finance_utils

class StrategyReportGenerator:
    """Generate PDF reports for strategy analysis results."""
    
    def __init__(self, ticker):
        self.ticker = ticker
        
    def generate_basic_report(self, results, filename=None):
        """Generate PDF report for basic strategy comparison."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_report_{self.ticker}_{timestamp}.pdf"
        
        with PdfPages(filename) as pdf:
            # Page 1: Summary
            self._create_summary_page(pdf, results)
            
            # Page 2: Portfolio Performance Chart
            self._create_portfolio_chart_page(pdf, results)
            
            # Page 3: Risk Metrics
            self._create_risk_metrics_page(pdf, results)
        
        return filename
    
    def generate_full_report(self, mr_results, mom_results, mr_best_params, mom_best_params, filename=None):
        """Generate comprehensive PDF report for full parameter exploration."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"full_analysis_report_{self.ticker}_{timestamp}.pdf"
        
        with PdfPages(filename) as pdf:
            # Page 1: Executive Summary
            self._create_executive_summary_page(pdf, mr_results, mom_results, mr_best_params, mom_best_params)
            
            # Page 2: Mean Reversion Analysis
            self._create_mean_reversion_analysis_page(pdf, mr_results, mr_best_params)
            
            # Page 3: Momentum Analysis
            self._create_momentum_analysis_page(pdf, mom_results, mom_best_params)
            
            # Page 4: Best Strategy Comparison
            self._create_best_strategies_comparison_page(pdf, mr_results, mom_results, mr_best_params, mom_best_params)
        
        return filename
    
    def _create_summary_page(self, pdf, results):
        """Create summary page for basic report."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Title
        fig.suptitle(f'Strategy Analysis Report - {self.ticker}', fontsize=20, fontweight='bold')
        
        # Report metadata
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ax.text(0.1, 0.9, f'Report Generated: {report_date}', fontsize=12, transform=ax.transAxes)
        ax.text(0.1, 0.85, f'Ticker: {self.ticker}', fontsize=12, fontweight='bold', transform=ax.transAxes)
        
        # Strategy results
        y_pos = 0.75
        ax.text(0.1, y_pos, 'STRATEGY PERFORMANCE SUMMARY', fontsize=16, fontweight='bold', transform=ax.transAxes)
        
        y_pos -= 0.08
        for strategy_name, data in results.items():
            strategy_title = strategy_name.replace('_', ' ').title()
            ax.text(0.1, y_pos, f'{strategy_title}:', fontsize=14, fontweight='bold', transform=ax.transAxes)
            
            y_pos -= 0.05
            sharpe = data['sharpe']
            if sharpe is not None:
                ax.text(0.15, y_pos, f'Sharpe Ratio: {sharpe:.4f}', fontsize=12, transform=ax.transAxes)
            else:
                ax.text(0.15, y_pos, 'Sharpe Ratio: Unable to calculate', fontsize=12, transform=ax.transAxes)
            
            y_pos -= 0.04
            drawdown = data['drawdown']['max_drawdown']
            if drawdown is not None:
                ax.text(0.15, y_pos, f'Max Drawdown: {drawdown:.2%}', fontsize=12, transform=ax.transAxes)
            else:
                ax.text(0.15, y_pos, 'Max Drawdown: N/A', fontsize=12, transform=ax.transAxes)
            
            # Parameters
            y_pos -= 0.04
            params = data['params']
            param_text = ', '.join([f'{k.title()}: {v}' for k, v in params.items()])
            ax.text(0.15, y_pos, f'Parameters: {param_text}', fontsize=12, transform=ax.transAxes)
            
            y_pos -= 0.08
        
        # Winner determination
        sharpes = [data['sharpe'] for data in results.values() if data['sharpe'] is not None]
        if sharpes:
            best_strategy = max(results.keys(), key=lambda k: results[k]['sharpe'] if results[k]['sharpe'] else -np.inf)
            ax.text(0.1, y_pos, f'BEST PERFORMING STRATEGY: {best_strategy.replace("_", " ").title()}', 
                   fontsize=14, fontweight='bold', color='green', transform=ax.transAxes)

            # Today's suggestion from the best-performing strategy
            try:
                y_pos -= 0.06
                rec = finance_utils.latest_trade_recommendation(results[best_strategy]['data'], ticker=self.ticker)
                if rec and rec.get('as_of_date') is not None:
                    date_str = rec['as_of_date'].strftime('%Y-%m-%d') if hasattr(rec['as_of_date'], 'strftime') else str(rec['as_of_date'])
                    price_str = f" at {rec['price']:.2f}" if rec.get('price') is not None else ""
                    ax.text(0.1, y_pos, f"TODAY'S SUGGESTION: {rec['action']} ({rec['state']}) as of {date_str}{price_str}",
                            fontsize=12, fontweight='bold', color='black', transform=ax.transAxes)
                    y_pos -= 0.035
                    ax.text(0.1, y_pos, "Note: This is not financial advice.", fontsize=10, color='dimgray', transform=ax.transAxes)
            except Exception:
                pass
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_portfolio_chart_page(self, pdf, results):
        """Create portfolio performance chart page."""
        fig, ax = plt.subplots(figsize=(11, 8.5))
        
        for strategy_name, data in results.items():
            portfolio_data = data['data']
            sharpe = data.get('sharpe')
            drawdown = None
            if isinstance(data.get('drawdown'), dict):
                drawdown = data['drawdown'].get('max_drawdown')

            label = f"{strategy_name.replace('_', ' ').title()}"
            metrics = []
            if sharpe is not None:
                metrics.append(f"Sharpe: {sharpe:.3f}")
            if drawdown is not None:
                metrics.append(f"DD: {drawdown:.2%}")
            if metrics:
                label += " (" + ", ".join(metrics) + ")"

            ax.plot(portfolio_data.index, portfolio_data['PortfolioValue'], label=label, linewidth=2)
        
        ax.set_title(f'Portfolio Value Evolution - {self.ticker}', fontsize=16, fontweight='bold')
        ax.set_ylabel('Portfolio Value', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_risk_metrics_page(self, pdf, results):
        """Create risk metrics comparison page."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.5, 11))
        
        # Sharpe Ratio Comparison
        strategies = list(results.keys())
        sharpe_ratios = [results[s]['sharpe'] if results[s]['sharpe'] else 0 for s in strategies]
        strategy_labels = [s.replace('_', ' ').title() for s in strategies]
        
        bars1 = ax1.bar(strategy_labels, sharpe_ratios, color=['blue', 'red'])
        ax1.set_title('Sharpe Ratio Comparison', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Sharpe Ratio')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars1, sharpe_ratios):
            if value != 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{value:.3f}', ha='center', va='bottom')
        
        # Max Drawdown Comparison
        drawdowns = [results[s]['drawdown']['max_drawdown'] if results[s]['drawdown']['max_drawdown'] else 0 for s in strategies]
        bars2 = ax2.bar(strategy_labels, drawdowns, color=['blue', 'red'])
        ax2.set_title('Maximum Drawdown Comparison', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Max Drawdown')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis as percentage
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
        
        # Add value labels on bars
        for bar, value in zip(bars2, drawdowns):
            if value != 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                        f'{value:.2%}', ha='center', va='bottom')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_executive_summary_page(self, pdf, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create executive summary for full analysis report."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Title
        fig.suptitle(f'Comprehensive Strategy Analysis - {self.ticker}', fontsize=18, fontweight='bold')
        
        # Report metadata
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ax.text(0.1, 0.9, f'Report Generated: {report_date}', fontsize=12, transform=ax.transAxes)
        
        y_pos = 0.8
        
        # Mean Reversion Summary
        ax.text(0.1, y_pos, 'MEAN REVERSION STRATEGY', fontsize=16, fontweight='bold', transform=ax.transAxes)
        y_pos -= 0.05
        
        if mr_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            ax.text(0.15, y_pos, f'Best Parameters: Window={mr_best_params[0]}, Threshold={mr_best_params[1]:.3f}', 
                   fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            ax.text(0.15, y_pos, f'Sharpe Ratio: {best_mr["Sharpe_Ratio"]:.4f}', fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            if best_mr['Max_Drawdown']:
                ax.text(0.15, y_pos, f'Max Drawdown: {best_mr["Max_Drawdown"]:.2%}', fontsize=12, transform=ax.transAxes)
        
        y_pos -= 0.08
        
        # Momentum Summary
        ax.text(0.1, y_pos, 'MOMENTUM STRATEGY', fontsize=16, fontweight='bold', transform=ax.transAxes)
        y_pos -= 0.05
        
        if mom_best_params:
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            ax.text(0.15, y_pos, f'Best Parameter: Window={mom_best_params}', fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            ax.text(0.15, y_pos, f'Sharpe Ratio: {best_mom["Sharpe_Ratio"]:.4f}', fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            if best_mom['Max_Drawdown']:
                ax.text(0.15, y_pos, f'Max Drawdown: {best_mom["Max_Drawdown"]:.2%}', fontsize=12, transform=ax.transAxes)
        
        # Overall recommendation
        y_pos -= 0.1
        ax.text(0.1, y_pos, 'RECOMMENDATION', fontsize=16, fontweight='bold', color='green', transform=ax.transAxes)
        y_pos -= 0.05
        
        if mr_best_params and mom_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            if best_mr['Sharpe_Ratio'] > best_mom['Sharpe_Ratio']:
                ax.text(0.15, y_pos, f'Mean Reversion strategy is recommended', fontsize=12, fontweight='bold', transform=ax.transAxes)
            else:
                ax.text(0.15, y_pos, f'Momentum strategy is recommended', fontsize=12, fontweight='bold', transform=ax.transAxes)

            # Today's suggestion from the higher-Sharpe best strategy
            try:
                y_pos -= 0.06
                preferred = best_mr if best_mr['Sharpe_Ratio'] >= best_mom['Sharpe_Ratio'] else best_mom
                rec = finance_utils.latest_trade_recommendation(preferred['Data'], ticker=self.ticker)
                if rec and rec.get('as_of_date') is not None:
                    date_str = rec['as_of_date'].strftime('%Y-%m-%d') if hasattr(rec['as_of_date'], 'strftime') else str(rec['as_of_date'])
                    price_str = f" at {rec['price']:.2f}" if rec.get('price') is not None else ""
                    ax.text(0.15, y_pos, f"TODAY'S SUGGESTION: {rec['action']} ({rec['state']}) as of {date_str}{price_str}",
                            fontsize=12, fontweight='bold', color='black', transform=ax.transAxes)
                    y_pos -= 0.035
                    ax.text(0.15, y_pos, "Note: This is not financial advice.", fontsize=10, color='dimgray', transform=ax.transAxes)
            except Exception:
                pass
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_mean_reversion_analysis_page(self, pdf, mr_results, mr_best_params):
        """Create mean reversion detailed analysis page."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Mean Reversion Strategy Analysis', fontsize=16, fontweight='bold')
        
        # Convert results to DataFrame
        results_df = pd.DataFrame([
            {'Window': r['Window'], 'Threshold': r['Threshold'], 'Sharpe_Ratio': r['Sharpe_Ratio'], 'Max_Drawdown': r['Max_Drawdown']} 
            for r in mr_results
        ])
        
        # Sharpe Ratio Heatmap
        sharpe_pivot = results_df.pivot(index='Window', columns='Threshold', values='Sharpe_Ratio')
        im1 = ax1.imshow(sharpe_pivot.values, cmap='RdYlGn', aspect='auto')
        ax1.set_title('Sharpe Ratio Heatmap')
        ax1.set_xticks(range(len(sharpe_pivot.columns)))
        ax1.set_xticklabels([f'{x:.3f}' for x in sharpe_pivot.columns])
        ax1.set_yticks(range(len(sharpe_pivot.index)))
        ax1.set_yticklabels(sharpe_pivot.index)
        ax1.set_xlabel('Threshold')
        ax1.set_ylabel('Window')
        plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
        
        # Max Drawdown Heatmap
        dd_pivot = results_df.pivot(index='Window', columns='Threshold', values='Max_Drawdown')
        im2 = ax2.imshow(dd_pivot.values, cmap='RdYlGn_r', aspect='auto')
        ax2.set_title('Max Drawdown Heatmap')
        ax2.set_xticks(range(len(dd_pivot.columns)))
        ax2.set_xticklabels([f'{x:.3f}' for x in dd_pivot.columns])
        ax2.set_yticks(range(len(dd_pivot.index)))
        ax2.set_yticklabels(dd_pivot.index)
        ax2.set_xlabel('Threshold')
        ax2.set_ylabel('Window')
        plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
        
        # Performance by Window
        window_performance = results_df.groupby('Window')['Sharpe_Ratio'].mean()
        ax3.bar(window_performance.index, window_performance.values)
        ax3.set_title('Average Sharpe by Window')
        ax3.set_xlabel('Window Size')
        ax3.set_ylabel('Average Sharpe Ratio')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Performance by Threshold
        threshold_performance = results_df.groupby('Threshold')['Sharpe_Ratio'].mean()
        ax4.bar(threshold_performance.index, threshold_performance.values)
        ax4.set_title('Average Sharpe by Threshold')
        ax4.set_xlabel('Threshold')
        ax4.set_ylabel('Average Sharpe Ratio')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_momentum_analysis_page(self, pdf, mom_results, mom_best_params):
        """Create momentum strategy detailed analysis page."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Momentum Strategy Analysis', fontsize=16, fontweight='bold')
        
        # Convert results to DataFrame
        results_df = pd.DataFrame([
            {'Window': r['Window'], 'Sharpe_Ratio': r['Sharpe_Ratio'], 'Max_Drawdown': r['Max_Drawdown']} 
            for r in mom_results
        ])
        
        # Performance by Window
        ax1.bar(results_df['Window'], results_df['Sharpe_Ratio'], color='blue', alpha=0.7)
        ax1.set_title('Sharpe Ratio by Window Size')
        ax1.set_xlabel('Window Size')
        ax1.set_ylabel('Sharpe Ratio')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Mark best parameter
        if mom_best_params:
            best_sharpe = results_df[results_df['Window'] == mom_best_params]['Sharpe_Ratio'].iloc[0]
            ax1.bar(mom_best_params, best_sharpe, color='green', alpha=0.9, label='Best')
            ax1.legend()
        
        # Max Drawdown by Window
        ax2.bar(results_df['Window'], results_df['Max_Drawdown'], color='red', alpha=0.7)
        ax2.set_title('Max Drawdown by Window Size')
        ax2.set_xlabel('Window Size')
        ax2.set_ylabel('Max Drawdown')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
        
        # Risk-Return Scatter
        ax3.scatter(results_df['Max_Drawdown'], results_df['Sharpe_Ratio'], s=100, alpha=0.7)
        ax3.set_xlabel('Max Drawdown')
        ax3.set_ylabel('Sharpe Ratio')
        ax3.set_title('Risk-Return Profile')
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
        
        # Add window labels to scatter points
        for _, row in results_df.iterrows():
            ax3.annotate(f'W{int(row["Window"])}', (row['Max_Drawdown'], row['Sharpe_Ratio']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Summary table
        ax4.axis('tight')
        ax4.axis('off')
        table_data = results_df.round(4)
        table_data['Max_Drawdown'] = table_data['Max_Drawdown'].apply(lambda x: f'{x:.2%}' if pd.notna(x) else 'N/A')
        ax4.table(cellText=table_data.values, colLabels=table_data.columns, cellLoc='center', loc='center')
        ax4.set_title('Summary Table')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_best_strategies_comparison_page(self, pdf, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create comparison page for best strategies from each type."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle('Best Strategy Comparison', fontsize=16, fontweight='bold')
        
        if mr_best_params and mom_best_params:
            # Get best results
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            # Portfolio comparison
            # Build labels with Sharpe and Drawdown
            mr_metrics = []
            if best_mr.get('Sharpe_Ratio') is not None:
                mr_metrics.append(f"Sharpe: {best_mr['Sharpe_Ratio']:.3f}")
            if best_mr.get('Max_Drawdown') is not None:
                mr_metrics.append(f"DD: {best_mr['Max_Drawdown']:.2%}")
            mr_label = f"Mean Reversion (W={mr_best_params[0]}, T={mr_best_params[1]:.3f})"
            if mr_metrics:
                mr_label += " (" + ", ".join(mr_metrics) + ")"

            mom_metrics = []
            if best_mom.get('Sharpe_Ratio') is not None:
                mom_metrics.append(f"Sharpe: {best_mom['Sharpe_Ratio']:.3f}")
            if best_mom.get('Max_Drawdown') is not None:
                mom_metrics.append(f"DD: {best_mom['Max_Drawdown']:.2%}")
            mom_label = f"Momentum (W={mom_best_params})"
            if mom_metrics:
                mom_label += " (" + ", ".join(mom_metrics) + ")"

            ax1.plot(best_mr['Data'].index, best_mr['Data']['PortfolioValue'], label=mr_label, linewidth=2)
            ax1.plot(best_mom['Data'].index, best_mom['Data']['PortfolioValue'], label=mom_label, linewidth=2)
            ax1.set_title('Portfolio Value Evolution')
            ax1.set_ylabel('Portfolio Value')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Performance metrics comparison
            categories = ['Sharpe Ratio', 'Max Drawdown']
            mr_values = [best_mr['Sharpe_Ratio'], best_mr['Max_Drawdown']]
            mom_values = [best_mom['Sharpe_Ratio'], best_mom['Max_Drawdown']]
            
            x = np.arange(len(categories))
            width = 0.35
            
            ax2.bar(x - width/2, [mr_values[0], -mr_values[1]], width, 
                   label='Mean Reversion', color='blue', alpha=0.7)
            ax2.bar(x + width/2, [mom_values[0], -mom_values[1]], width, 
                   label='Momentum', color='red', alpha=0.7)
            
            ax2.set_title('Performance Metrics Comparison')
            ax2.set_xticks(x)
            ax2.set_xticklabels(['Sharpe Ratio', 'Max Drawdown (Inverted)'])
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Price with signals (Mean Reversion)
            mr_data = best_mr['Data']
            ax3.plot(mr_data.index, mr_data[f'Close_{self.ticker}'], label=f'{self.ticker} Price', color='black')
            buy_signals = mr_data[mr_data['Position'] == 1]
            sell_signals = mr_data[mr_data['Position'] == -1]
            ax3.scatter(buy_signals.index, buy_signals[f'Close_{self.ticker}'], 
                       marker='^', color='green', s=30, label='Buy', alpha=0.7)
            ax3.scatter(sell_signals.index, sell_signals[f'Close_{self.ticker}'], 
                       marker='v', color='red', s=30, label='Sell', alpha=0.7)
            ax3.set_title('Mean Reversion Signals')
            ax3.legend(fontsize=8)
            ax3.grid(True, alpha=0.3)
            
            # Price with signals (Momentum)
            mom_data = best_mom['Data']
            ax4.plot(mom_data.index, mom_data[f'Close_{self.ticker}'], label=f'{self.ticker} Price', color='black')
            buy_signals = mom_data[mom_data['Position'] == 1]
            sell_signals = mom_data[mom_data['Position'] == -1]
            ax4.scatter(buy_signals.index, buy_signals[f'Close_{self.ticker}'], 
                       marker='^', color='green', s=30, label='Buy', alpha=0.7)
            ax4.scatter(sell_signals.index, sell_signals[f'Close_{self.ticker}'], 
                       marker='v', color='red', s=30, label='Sell', alpha=0.7)
            ax4.set_title('Momentum Signals')
            ax4.legend(fontsize=8)
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

def prompt_for_report_generation(report_type, results=None, mr_results=None, mom_results=None, 
                                mr_best_params=None, mom_best_params=None, ticker=None):
    """Prompt user to generate PDF report and handle the generation."""
    try:
        generate = input(f"\nGenerate PDF report? (y/N): ").strip().lower()
        if generate in ['y', 'yes']:
            print("Generating PDF report...")
            
            report_gen = StrategyReportGenerator(ticker)
            
            if report_type == 'basic' and results:
                filename = report_gen.generate_basic_report(results)
            elif report_type == 'full' and mr_results and mom_results:
                filename = report_gen.generate_full_report(mr_results, mom_results, mr_best_params, mom_best_params)
            else:
                print("ERROR: Invalid report configuration")
                return
            
            print(f"PDF report generated: {filename}")
            
            # Check if file was created and show file size
            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / 1024  # Size in KB
                print(f"Report saved successfully ({file_size:.1f} KB)")
            else:
                print("ERROR: Report file was not created")
                
    except (EOFError, KeyboardInterrupt):
        print("\nSkipping report generation.")
    except Exception as e:
        print(f"ERROR generating report: {e}")