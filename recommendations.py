def generate_recommendations(
    habits,
    total_spending,
    budget,
    goal,
    
):

    recommendations = []


    category_spending = {}


    for habit in habits:

        category = habit["category"]
        cost = habit["cost"]

        category_spending[category] = (
            category_spending.get(category, 0)
            + cost
        )
    
    for habit in habits:
        
        monthly = habit["cost"]

        saving = monthly * 0.5

        recommendations.append(
           {
            "type": "success",
            "message":
            f"💡 Reducing **{habit['habit']}** by 50% saves approximately ₹{saving:,.0f} every month."
           }
        )

        break


    # Budget recommendation

    if budget > 0:

        if total_spending > budget:

            recommendations.append(
                {
                    "type": "warning",
                    "message":
                    f"⚠️ You are ₹{total_spending-budget:,.0f} over your budget. Try reducing unnecessary habits."
                }
            )

        else:

            recommendations.append(
                {
                    "type": "success",
                    "message":
                    "✅ You are within your monthly budget!"
                }
            )


    # Highest category saving suggestion

    if category_spending:

        highest = max(
            category_spending,
            key=category_spending.get
        )

        amount = category_spending[highest]

        saving = amount * 0.25


        recommendations.append(
            {
                "type": "warning",
                "message":
                f"💰 {highest} costs ₹{amount:,.0f}/month. Reducing it by 25% can save ₹{saving:,.0f}/month."
            }
        )


    # Subscription recommendation

    subscriptions = [
        h for h in habits
        if h["category"] == "Subscriptions"
    ]


    if subscriptions:

        subscription_cost = sum(
            h["cost"]
            for h in subscriptions
        )

        recommendations.append(
            {
                "type": "warning",
                "message":
                f"📺 Your subscriptions cost ₹{subscription_cost:,.0f}/month. Removing one unused subscription can save money."
            }
        )
    # ==========================================
    # GOAL BASED RECOMMENDATIONS
    # ==========================================

    if goal == "Save More":
        
        recommendations.append(
        {
            "type": "success",
            "message":
            "💰 Keep reducing unnecessary expenses to maximize your monthly savings."
        }
    )


    elif goal == "Reduce Spending":
        
        recommendations.append(
        {
            "type": "warning",
            "message":
            "📉 Focus on cutting your highest-cost habit first for the biggest impact."
        }
    )


    elif goal == "Build Emergency Fund":
        recommendations.append(
        {
            "type": "info",
            "message":
            "🚨 Aim to save 3–6 months of living expenses for emergencies."
        }
    )


    elif goal == "Travel":
        recommendations.append(
        {
            "type": "success",
            "message":
            "✈️ Every rupee you save today brings your next vacation closer."
        }
    )


    elif goal == "Buy a Laptop":
        recommendations.append(
        {
            "type": "success",
            "message":
            "💻 Redirect your habit savings into a dedicated laptop fund."
        }
    )


    elif goal == "Buy a Vehicle":
        recommendations.append(
        {
            "type": "info",
            "message":
            "🚗 Consistent monthly savings can help you build a vehicle down payment."
        }
    )


    elif goal == "Buy a House":
        
        recommendations.append(
        {
            "type": "info",
            "message":
            "🏠 Long-term investing can help you accumulate a home down payment."
        }
    )


    elif goal == "Invest More":
        recommendations.append(
        {
            "type": "success",
            "message":
            "📈 Try investing your habit savings every month to grow your wealth."
        }
    )


    elif goal == "Education":
        
        recommendations.append(
        {
            "type": "info",
            "message":
            "🎓 Small monthly savings today can fund future courses and certifications."
        }
    )

    return recommendations