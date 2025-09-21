// nutrition/static/admin/nutrition/cost_popup.js
function showCostInfo(recipeId) {
    const margin = prompt('마진율을 입력하세요 (예: 150 = 50% 마진)', '150');
    if (!margin || isNaN(margin)) return;
    
    fetch(`/api/recipes/${recipeId}/cost-simple?margin=${margin}`)
        .then(response => response.json())
        .then(data => {
            const content = `
                <div style="font-family: system-ui; line-height: 1.6; max-width: 500px;">
                    <h3 style="color: #1f2937; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;">
                        💰 ${data.recipe_id ? '레시피' : ''} 원가 분석
                    </h3>
                    
                    <div style="background: #f8fafc; padding: 12px; border-radius: 6px; margin: 12px 0;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                            <div><strong>원재료비:</strong> ${data.total_cost?.toLocaleString() || 0}원</div>
                            <div><strong>손실률 적용:</strong> ${data.adjusted_total_cost?.toLocaleString() || 0}원</div>
                            <div><strong>조각당 원가:</strong> ${data.cost_per_piece?.toLocaleString() || 0}원</div>
                            <div><strong>권장 조각가:</strong> ${data.suggested_price_per_piece?.toLocaleString() || 0}원</div>
                        </div>
                    </div>
                    
                    <div style="font-size: 12px; color: #6b7280;">
                        <p>• 수율: ${data.yield_rate || 100}% (${data.servings || 1}조각 기준)</p>
                        <p>• 마진율: ${data.margin_percent || 150}% (${((data.margin_percent || 150) - 100)}% 이익)</p>
                    </div>
                    
                    ${data.items_cost && data.items_cost.length > 0 ? `
                    <details style="margin-top: 12px;">
                        <summary style="cursor: pointer; font-weight: 500; color: #374151;">재료별 원가 상세</summary>
                        <div style="margin-top: 8px; max-height: 200px; overflow-y: auto;">
                            ${data.items_cost.map(item => `
                                <div style="padding: 4px; border-bottom: 1px solid #e5e7eb; font-size: 12px;">
                                    <span style="font-weight: 500;">${item.ingredient}</span>: 
                                    ${item.amount_g}g × ${item.price_per_100g}원/100g = ${item.cost?.toLocaleString() || 0}원
                                </div>
                            `).join('')}
                        </div>
                    </details>
                    ` : ''}
                </div>
            `;
            
            showModal('원가 정보', content);
        })
        .catch(error => {
            alert('원가 정보를 불러오는데 실패했습니다: ' + error.message);
        });
}

function showModal(title, content) {
    // 기존 모달 제거
    const existingModal = document.getElementById('cost-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 모달 생성
    const modal = document.createElement('div');
    modal.id = 'cost-modal';
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.5); z-index: 10000; 
        display: flex; align-items: center; justify-content: center;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white; padding: 20px; border-radius: 8px; 
        max-width: 600px; max-height: 80vh; overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    `;
    
    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h2 style="margin: 0; color: #1f2937;">${title}</h2>
            <button onclick="document.getElementById('cost-modal').remove()" 
                    style="background: none; border: none; font-size: 24px; cursor: pointer; color: #6b7280;">×</button>
        </div>
        ${content}
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // 배경 클릭시 닫기
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}