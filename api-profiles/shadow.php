<!DOCTYPE html>
<html lang="en-US">
<head>
    <title>Switch to shadow profiles</title>
    <meta charset="utf-8">
    <link rel="stylesheet" href="table.css">
    <script type="text/javascript">
        function selectAll(){
            var items=document.getElementsByName('deletep[]');
            for(var i=0; i<items.length; i++){
                if(items[i].type=='checkbox')
                    items[i].checked=true;
            }
        }
		function UnSelectAll(){
			var items=document.getElementsByName('deletep[]');
			for(var i=0; i<items.length; i++){
				if(items[i].type=='checkbox')
					items[i].checked=false;
			}
		}
    </script>
</head>
<body>  
    <?php include 'main.php';?>            
    <section class="datagrid">
        <!--for table wrap-->
        <h1>All profiles</h1>
        <form action="main.php?action=modify" method="post">
        <table cellpadding="0" cellspacing="0" border="0">
            <thead>
            <tr>
                <th>Convert?</th>
                <th>Name</th>
                <th>Type</th>
                <th>Group</th>
                <th>Description</th>
            </tr>
            </thead>
            <tbody>
            <?php all_profiles($profile1); ?>
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="5">
                        <input type="button" onclick='selectAll()' value="Select All"/>
                        <input type="button" onclick='UnSelectAll()' value="Unselect All"/>
                        <div align="right"><input type="submit" value="Submit" /></div>
                    </td>
                </tr>
            </tfoot>
        </table>
        </form>
    </section>
</body>